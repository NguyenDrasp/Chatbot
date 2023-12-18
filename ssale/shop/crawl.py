import requests
from bs4 import BeautifulSoup

def get_des(url):
    # Tải nội dung của trang web
    response = requests.get(url)
    descrip = ''
    # Kiểm tra xem yêu cầu đã thành công hay không (status code 200 là thành công)
    if response.status_code == 200:
        # Sử dụng BeautifulSoup để phân tích nội dung HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tìm tất cả các thẻ 'p' có class là 'desp2 more'
        desp2_paragraphs = soup.find_all('p', class_='desp2 more')
        
        # In ra văn bản trong các thẻ 'p' này
        for paragraph in desp2_paragraphs:
            descrip = descrip + '/n' + paragraph.get_text()
            print(descrip)
    else:
        print("Không thể tải trang web")

# Gọi hàm get_desp2_text với URL của trang web cần lấy thông tin
    return descrip