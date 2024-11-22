from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Optional, Dict, Any
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import re
# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Transaction API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class DataManager:
    def __init__(self):
        self.df = None
        self.load_data()

    def load_data(self):
        try:
            # Đọc file CSV với các kiểu dữ liệu được chỉ định
            self.df = pd.read_csv('chuyen_khoan.csv', dtype={
                'credit': 'float64',
                'date_time': 'str',
                'detail': 'str',
            })
            
            # Xử lý cột date_time
            if 'date_time' in self.df.columns:
                self.df[['date', 'trans_id']] = self.df['date_time'].str.split('_', expand=True)
                self.df['date'] = pd.to_datetime(self.df['date'], format='%d/%m/%Y', errors='coerce')
            
            # Chuyển đổi và làm sạch cột credit
            self.df['credit'] = pd.to_numeric(self.df['credit'], errors='coerce')
            
            # Loại bỏ các dòng có giá trị NaN trong các cột quan trọng
            self.df = self.df.dropna(subset=['credit', 'date'])
            logger.info(f"Data loaded successfully. Shape: {self.df.shape}")
            
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            self.df = pd.DataFrame()
            raise

    def paginate_results(self, df: pd.DataFrame, page: int = 1, page_size: int = 100) -> pd.DataFrame:
        try:
            start = (page - 1) * page_size
            end = start + page_size
            return df.iloc[start:end]
        except Exception as e:
            logger.error(f"Pagination error: {str(e)}")
            raise

    def prepare_response(self, df: pd.DataFrame, page: int, page_size: int) -> Dict[str, Any]:
        total_records = len(df)
        total_pages = -(-total_records // page_size)  # Ceiling division
        paginated_df = self.paginate_results(df, page, page_size)
        # Convert date to string format before sending response
        paginated_df['date'] = paginated_df['date'].dt.strftime('%d/%m/%Y')
        
        return {
            "total_records": total_records,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "data": paginated_df.to_dict(orient="records")
        }
    def apply_filters(self, 
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None,
                     keywords: Optional[str] = None,
                     amount_range: Optional[str] = None,
                     min_amount: Optional[float] = None,
                     max_amount: Optional[float] = None) -> pd.DataFrame:
        """
        Apply multiple filters to the dataframe
        """
        filtered_df = self.df.copy()
        
        # Date range filter
        if start_date and end_date:
            try:
                start = pd.to_datetime(start_date, format='%d/%m/%Y')
                end = pd.to_datetime(end_date, format='%d/%m/%Y')
                filtered_df = filtered_df[
                    (filtered_df['date'] >= start) & 
                    (filtered_df['date'] <= end)
                ]
            except ValueError as e:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid date format. Use DD/MM/YYYY"
                )

        # Keywords filter
        if keywords:
            filtered_df = filtered_df[
                filtered_df['detail'].str.contains(keywords, case=False, na=False)
            ]

        # Amount range filter
        if amount_range:
            if amount_range == "under_5m":
                filtered_df = filtered_df[filtered_df['credit'] < 5000000]
            elif amount_range == "5m_10m":
                filtered_df = filtered_df[
                    (filtered_df['credit'] >= 5000000) & 
                    (filtered_df['credit'] <= 10000000)
                ]
            elif amount_range == "10m_50m":
                filtered_df = filtered_df[
                    (filtered_df['credit'] > 10000000) & 
                    (filtered_df['credit'] <= 50000000)
                ]
            elif amount_range == "50m_100m":
                filtered_df = filtered_df[
                    (filtered_df['credit'] > 50000000) & 
                    (filtered_df['credit'] <= 100000000)
                ]
            elif amount_range == "above_100m":
                filtered_df = filtered_df[filtered_df['credit'] > 100000000]

        # Custom amount range filter
        if min_amount is not None and max_amount is not None:
            filtered_df = filtered_df[
                (filtered_df['credit'] >= min_amount) & 
                (filtered_df['credit'] <= max_amount)
            ]
        elif min_amount is not None:
            filtered_df = filtered_df[filtered_df['credit'] >= min_amount]
        elif max_amount is not None:
            filtered_df = filtered_df[filtered_df['credit'] <= max_amount]

        return filtered_df
    def search_multiple_fields(self, search_text: str) -> pd.DataFrame:
        """
        Tìm kiếm trong nhiều trường dữ liệu
        """
        if not search_text:
            return self.df
            
        df = self.df.copy()
        
        # Chuyển tất cả dữ liệu về string để tìm kiếm
        df['credit_str'] = df['credit'].astype(str)
        df['date_str'] = df['date'].dt.strftime('%d/%m/%Y')
        
        # Chuẩn bị search_text
        search_text = search_text.lower().strip()
        
        # Tìm kiếm trong tất cả các trường
        mask = (
            df['detail'].str.lower().str.contains(search_text, na=False) |
            df['trans_id'].str.lower().str.contains(search_text, na=False) |
            df['credit_str'].str.contains(search_text, na=False) |
            df['date_str'].str.contains(search_text, na=False)
        )
        
        # Xử lý tìm kiếm số tiền dạng "5tr", "5m", "5 triệu"
        if any(x in search_text for x in ['tr', 'm', 'triệu', 'trieu']):
            try:
                # Chuyển đổi text sang số
                amount = self._convert_amount_text(search_text)
                if amount:
                    # Tìm kiếm với sai số ±10%
                    lower_bound = amount * 0.9
                    upper_bound = amount * 1.1
                    amount_mask = (df['credit'] >= lower_bound) & (df['credit'] <= upper_bound)
                    mask = mask | amount_mask
            except ValueError:
                pass
                
        return df[mask].drop(columns=['credit_str', 'date_str'])
    
    def _convert_amount_text(self, text: str) -> float:
        """
        Chuyển đổi text số tiền sang số
        Ví dụ: "5tr" -> 5000000, "5m" -> 5000000
        """
        # Xóa khoảng trắng và chuyển về lowercase
        text = text.lower().replace(' ', '')
        
        # Các pattern phổ biến
        patterns = {
            r'(\d+)tr': lambda x: float(x) * 1000000,
            r'(\d+)m': lambda x: float(x) * 1000000,
            r'(\d+)trieu': lambda x: float(x) * 1000000,
            r'(\d+)t': lambda x: float(x) * 1000000
        }
        
        for pattern, converter in patterns.items():
            match = re.search(pattern, text)
            if match:
                return converter(match.group(1))
        return None
# Unified filter endpoint


# You can keep the health check endpoint
# @app.get("/health")
# async def health_check():
#     return {"status": "OK"}

# Khởi tạo DataManager
data_manager = DataManager()

@app.get('/api/filter/date_range')
async def filter_by_date_range(
    start_date: str = Query(..., description="Start date in DD/MM/YYYY format"),
    end_date: str = Query(..., description="End date in DD/MM/YYYY format"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Items per page")
):
    try:
        logger.info(f"Date range filter request: {start_date} to {end_date}")
        
        # Chuyển đổi ngày
        start = pd.to_datetime(start_date, format='%d/%m/%Y')
        end = pd.to_datetime(end_date, format='%d/%m/%Y')
        # Lọc dữ liệu
        mask = (data_manager.df['date'] >= start) & (data_manager.df['date'] <= end)
        filtered_df = data_manager.df[mask]
        
        if filtered_df.empty:
            return JSONResponse(content={
                "total_records": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "data": []
            })
        
        response_data = data_manager.prepare_response(filtered_df, page, page_size)
        return JSONResponse(content=response_data)
        
    except ValueError as ve:
        logger.error(f"Date format error: {str(ve)}")
        raise HTTPException(status_code=400, detail="Invalid date format. Use DD/MM/YYYY")
    except Exception as e:
        logger.error(f"Error in date range filter: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get('/api/filter/amount_range')
async def filter_by_amount_range(
    min_amount: Optional[float] = Query(None, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, description="Maximum amount"),
    range_option: Optional[str] = Query(None, description="Predefined range option"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Items per page")
):
    try:
        logger.info(f"Amount range filter request: min={min_amount}, max={max_amount}, range_option={range_option}")
        
        # Tạo một bản sao để tránh ảnh hưởng đến dữ liệu gốc
        df_copy = data_manager.df.copy()
        
        # Xác định mask dựa trên các tham số
        if range_option == 'under_5m':
            mask = df_copy['credit'] < 5000000
        elif range_option == '5m_10m':
            mask = (df_copy['credit'] >= 5000000) & (df_copy['credit'] <= 10000000)
        elif range_option == '10m_15m':
             mask = (df_copy['credit'] >= 10000000) & (df_copy['credit'] <= 50000000)
        elif min_amount is not None and max_amount is not None:
            mask = (df_copy['credit'] >= min_amount) & (df_copy['credit'] <= max_amount)
        elif min_amount is not None:
            mask = df_copy['credit'] >= min_amount
        elif max_amount is not None:
            mask = df_copy['credit'] <= max_amount
        else:
            raise HTTPException(status_code=400, detail="Provide valid range parameters")
        
        filtered_df = df_copy[mask]
        
        if filtered_df.empty:
            return JSONResponse(content={
                "total_records": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "data": []
            })
        
        response_data = data_manager.prepare_response(filtered_df, page, page_size)
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Error in amount range filter: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get('/api/filter')
async def unified_filter(
    start_date: Optional[str] = Query(None, description="Start date (DD/MM/YYYY)"),
    end_date: Optional[str] = Query(None, description="End date (DD/MM/YYYY)"),
    keywords: Optional[str] = Query(None, description="Search across all fields"),
    amount_range: Optional[str] = Query(None, description="Predefined amount ranges"),
    min_amount: Optional[float] = Query(None, description="Minimum amount for custom range"),
    max_amount: Optional[float] = Query(None, description="Maximum amount for custom range"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Items per page")
):
    try:
        # Áp dụng tìm kiếm đa trường trước
        if keywords:
            filtered_df = data_manager.search_multiple_fields(keywords)
        else:
            filtered_df = data_manager.df.copy()
        
        # Áp dụng các bộ lọc khác
        if start_date and end_date:
            start = pd.to_datetime(start_date, format='%d/%m/%Y')
            end = pd.to_datetime(end_date, format='%d/%m/%Y')
            filtered_df = filtered_df[
                (filtered_df['date'] >= start) & 
                (filtered_df['date'] <= end)
            ]

        # Xử lý amount_range và min_amount/max_amount như cũ
        if amount_range:
            if amount_range == "under_5m":
                filtered_df = filtered_df[filtered_df['credit'] < 50000000]
            elif amount_range == "5m_10m":
                filtered_df = filtered_df[
                    (filtered_df['credit'] >= 50000000) & 
                    (filtered_df['credit'] <= 10000000)
                ]
            elif amount_range == "10m_50m":
                filtered_df = filtered_df[
                    (filtered_df['credit'] >= 10000000) & 
                    (filtered_df['credit'] <= 50000000)
                ]
            elif amount_range == "50m_100m":
                filtered_df = filtered_df[
                    (filtered_df['credit'] >= 50000000) &
                    (filtered_df['credit'] <= 100000000)
                ]
            elif amount_range == "above_100m":
                    filtered_df = filtered_df[filtered_df['credit'] > 100000000]
            # ... (giữ nguyên các range khác)

        if min_amount is not None and max_amount is not None:
            filtered_df = filtered_df[
                (filtered_df['credit'] >= min_amount) & 
                (filtered_df['credit'] <= max_amount)
            ]
        
        if filtered_df.empty:
            return JSONResponse(content={
                "total_records": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "data": []
            })

        return data_manager.prepare_response(filtered_df, page, page_size)

    except Exception as e:
        logger.error(f"Error in unified filter: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/health")
async def health_check():
    return {"status": "OK"}