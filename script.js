// Hàm để lọc theo khoảng thời gian
async function filterByDateRange() {
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;

    if (!startDate || !endDate) {
        alert("Please enter both start date and end date.");
        return;
    }

    // Populate the table with new data
    data.forEach(transaction => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${transaction.date_time}</td>
            <td>${transaction.trans_no}</td>
            <td>${transaction.credit}</td>
            <td>${transaction.debit}</td>
            <td>${transaction.detail}</td>
        `;
        tbody.appendChild(row);
    });
}

async function filterByKeyword() {
    const keyword = document.getElementById("keyword").value;
    const response = await fetch(`http://127.0.0.1:8000/api/filter/keyword?keyword=${encodeURIComponent(keyword)}`);
    const data = await response.json();
    displayResults(data);
}

async function filterByCredit() {
    const creditAmount = document.getElementById("creditAmount").value;
    const response = await fetch(`http://127.0.0.1:8000/api/filter/credit?amount=${encodeURIComponent(creditAmount)}`);
    const data = await response.json();
    displayResults(data);
}

async function filterByDate() {
    // Lấy giá trị ngày từ input (định dạng yyyy-mm-dd)
    const date = document.getElementById("date").value;

    // Chuyển đổi ngày từ yyyy-mm-dd sang dd/mm/yyyy
    const formattedDate = formatDate(date);

    // Gửi yêu cầu API với ngày đã chuyển đổi
    const response = await fetch(`http://127.0.0.1:8000/api/filter/date?date=${encodeURIComponent(formattedDate)}`);
    const data = await response.json();
    displayResults(data);
}

async function filterByRecipient() {
    const recipientName = document.getElementById("recipientName").value;
    const response = await fetch(`http://127.0.0.1:8000/api/filter/recipient?name=${encodeURIComponent(recipientName)}`);
    const data = await response.json();
    displayResults(data);
}

async function filterByDateTime() {
    const dateTime = document.getElementById("dateTime").value;
    const response = await fetch(`http://127.0.0.1:8000/api/filter/datetime?datetime=${encodeURIComponent(dateTime)}`);
    const data = await response.json();
    displayResults(data);
}

function formatDate(date) {
    const [year, month, day] = date.split("-");
    return `${day.padStart(2, '0')}/${month.padStart(2, '0')}/${year}`;
}


//feature
const API_BASE_URL = 'http://localhost:8000/api';
let currentPage = 1;
const pageSize = 100;
let totalPages = 0;
let activeAmountRange = null;

function toggleFilters() {
    const filterPanel = document.getElementById('filter_panel');
    filterPanel.classList.toggle('active');
}

// Add click handlers for amount range buttons
document.querySelectorAll('.amount-button').forEach(button => {
    button.addEventListener('click', function() {
        document.querySelectorAll('.amount-button').forEach(btn =>
            btn.classList.remove('active'));
        this.classList.add('active');
        activeAmountRange = this.dataset.range;

        // Clear custom range inputs when preset range is selected
        document.getElementById('min_amount').value = '';
        document.getElementById('max_amount').value = '';
    });
});

// Clear active range button when custom range is being input
document.getElementById('min_amount').addEventListener('input', clearActiveRangeButton);
document.getElementById('max_amount').addEventListener('input', clearActiveRangeButton);

function clearActiveRangeButton() {
    document.querySelectorAll('.amount-button').forEach(btn =>
        btn.classList.remove('active'));
    activeAmountRange = null;
}

async function applyFilters() {
    showLoading();

    const keyword = document.getElementById('search_keyword').value;
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;
    const minAmount = document.getElementById('min_amount').value;
    const maxAmount = document.getElementById('max_amount').value;

    let url = `${API_BASE_URL}/filter?page=${currentPage}&page_size=${pageSize}`;

    if (keyword) url += `&keywords=${encodeURIComponent(keyword)}`;
    if (startDate) url += `&start_date=${startDate}`;
    if (endDate) url += `&end_date=${endDate}`;
    if (activeAmountRange) url += `&amount_range=${activeAmountRange}`;
    if (minAmount) url += `&min_amount=${minAmount}`;
    if (maxAmount) url += `&max_amount=${maxAmount}`;

    try {
        const data = await fetchWithError(url);

        if (data.total_records === 0) {
            showNoData();
            return;
        }

        displayData(data.data);
        totalPages = data.total_pages;
        createPagination(currentPage, totalPages);
        hideLoading();
    } catch (error) {
        console.error('Error applying filters:', error);
    }
}

// Existing helper functions remain the same
function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('data_table').style.display = 'none';
    document.getElementById('no_data').style.display = 'none';
    document.getElementById('pagination').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('data_table').style.display = 'table';
    document.getElementById('pagination').style.display = 'flex';
}

function showNoData() {
    document.getElementById('no_data').style.display = 'block';
    document.getElementById('data_table').style.display = 'none';
    document.getElementById('pagination').style.display = 'none';
}

function formatAmount(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

// Existing display and pagination functions remain the same
function createPagination(currentPage, totalPages) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';

    const prevButton = document.createElement('button');
    prevButton.innerText = '←';
    prevButton.disabled = currentPage === 1;
    prevButton.onclick = () => changePage(currentPage - 1);
    pagination.appendChild(prevButton);

    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            const pageButton = document.createElement('button');
            pageButton.innerText = i;
            pageButton.disabled = i === currentPage;
            pageButton.onclick = () => changePage(i);
            pagination.appendChild(pageButton);
        } else if ((i === currentPage - 3 && currentPage > 4) ||
            (i === currentPage + 3 && currentPage < totalPages - 3)) {
            const ellipsis = document.createElement('span');
            ellipsis.innerText = '...';
            pagination.appendChild(ellipsis);
        }
    }

    const nextButton = document.createElement('button');
    nextButton.innerText = '→';
    nextButton.disabled = currentPage === totalPages;
    nextButton.onclick = () => changePage(currentPage + 1);
    pagination.appendChild(nextButton);
}

function displayData(data) {
    const tbody = document.getElementById('data_body');
    tbody.innerHTML = '';

    data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
                    <td>${item.date}</td>
                    <td>${item.trans_id}</td>
                    <td>${formatAmount(item.credit)}</td>
                    <td>${item.detail}</td>
                `;
        tbody.appendChild(row);
    });
}

async function fetchWithError(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while fetching data. Please try again.');
        hideLoading();
        showNoData();
        throw error;
    }
}


async function changePage(newPage) {
    if (newPage < 1 || newPage > totalPages) return;
    currentPage = newPage;
    await applyFilters();
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('data_table').style.display = 'none';
    document.getElementById('pagination').style.display = 'none';
});
document.getElementById('search_keyword').addEventListener('keyup', function(e) {
    if (e.key === 'Enter') {
        currentPage = 1;
        applyFilters();
    }
});

// Thêm hàm debounce để tránh gọi API quá nhiều
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Cập nhật placeholder của ô search để thông báo cho user
document.getElementById('search_keyword').placeholder =
    "Tìm theo ngày (DD/MM/YYYY), mã GD, nội dung, số tiền (5tr, 5m...)";
    async function searchByDetail() {
        const detailKeyword = document.getElementById('detail_search').value;
        
        if (!detailKeyword) {
            // If no keyword, reset to default view or show all
            currentPage = 1;
            await applyFilters();
            return;
        }
    
        showLoading();
    
        try {
            // Reset to first page when doing a new search
            currentPage = 1;
            
            // Use the new dedicated detail search endpoint
            const url = `${API_BASE_URL}/filter/detail?detail_keyword=${encodeURIComponent(detailKeyword)}&page=${currentPage}&page_size=${pageSize}`;
            
            const data = await fetchWithError(url);
    
            if (data.total_records === 0) {
                showNoData();
                return;
            }
    
            displayData(data.data);
            totalPages = data.total_pages;
            createPagination(currentPage, totalPages);
            hideLoading();
        } catch (error) {
            console.error('Error searching by detail:', error);
            hideLoading();
            showNoData();
        }
    }
    document.getElementById('detail_search').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            searchByDetail();
        }
    });
//them

flatpickr("#start_date", {
    dateFormat: "d/m/Y", // Định dạng DD/MM/YYYY
});

flatpickr("#end_date", {
    dateFormat: "d/m/Y",
});