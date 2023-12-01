# Chatbot     
cd vào Frontend   
thay đổi link ngrok đúng theo cú pháp trong .env , Chú ý là đừng thừa dấu / ở link    
docker build -t chatbot .    
docker run -p 3000:3000 chatbot    
