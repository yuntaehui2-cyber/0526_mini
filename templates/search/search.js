const tableBody = document.getElementById('contactTableBody');

// [기능 1] 주소록 목록을 백엔드에서 가져와 테이블에 그려주는 함수
function loadContacts(keyword = '') {
    fetch(`/api/contacts?keyword=${encodeURIComponent(keyword)}`)
        .then(res => {
            if (res.status === 403) {
                alert('로그인이 만료되었습니다.');
                location.href = '/login';
            }
            return res.json();
        })
        .then(data => {
            tableBody.innerHTML = ''; // 테이블 내용 비우기 (새로고침 방지)
            
            // 데이터 수신 후 테이블 동적 생성 (insertAdjacentHTML 활용)
            data.forEach(c => {
                const row = `<tr>
                    <td>${c.id}</td>
                    <td>${c.name}</td>
                    <td>${c.phone}</td>
                    <td>${c.address}</td>
                </tr>`;
                tableBody.insertAdjacentHTML('beforeend', row);
            });
        });
}

// 페이지가 처음 로드될 때 전체 목록 자동 조회
window.addEventListener('DOMContentLoaded', () => loadContacts());

// [기능 2] 검색 버튼 클릭 시 비동기 요청
document.getElementById('searchBtn').addEventListener('click', () => {
    const keyword = document.getElementById('searchKeyword').value;
    loadContacts(keyword);
});

// [기능 3] 연락처 추가 버튼 클릭 시 비동기 요청
document.getElementById('addBtn').addEventListener('click', () => {
    const name = document.getElementById('name').value;
    const phone = document.getElementById('phone').value;
    const address = document.getElementById('address').value;

    fetch('/api/contacts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, phone, address })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if (data.success) {
            // 입력창 비우기
            document.getElementById('name').value = '';
            document.getElementById('phone').value = '';
            document.getElementById('address').value = '';
            loadContacts(); // 데이터 등록 후 화면 새로고침 없이 표만 즉시 갱신
        }
    });
});

// [기능 4] 로그아웃 요청 로직
document.getElementById('logoutBtn').addEventListener('click', () => {
    fetch('/api/logout', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            location.href = '/login';
        });
});