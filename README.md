**1. Clone โปรเจคจาก GitHub**
- gh repo clone nantiwan47/CNStyleShop
- cd CNStyleShop

**2. สร้าง virtual environment สำหรับ Windows**  
- python -m venv venv
- .venv\Scripts\activate

**3. ติดตั้ง Python Dependencies**
- pip install -r requirements.txt

**4. เข้าไปในโฟลเดอร์ theme และ static_src และติดตั้ง npm dependencies**   
- cd theme
- cd static_src
- npm install

**5. กลับมาที่โฟลเดอร์หลักของโปรเจค** 
- cd ..
- cd ..

**6. เริ่มต้น Tailwind CSS**
- python manage.py tailwind start

**7. รัน Django Server**
- python manage.py runserver

