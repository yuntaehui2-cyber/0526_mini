document.getElementById('loginBtn').addEventListener('click', () => {
    const id = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // 백엔드가 만든 로그인 API 주소로 비동기(Fetch) 요청
    fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.href = '/'; // 로그인 성공 시 메인 주소록 페이지로 이동
        } else {
            alert(data.message);
        }
    })
    .catch(err => alert('로그인 통신 실패: ' + err));
});