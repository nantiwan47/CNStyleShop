# CN Style Shop Web Application

เว็บแอปพลิเคชันสำหรับขายเสื้อผ้าแฟชั่นออนไลน์จากประเทศจีน พัฒนาด้วย Django เป็น Framework หลักในการพัฒนา ร่วมกับฐานข้อมูล MySQL และใช้ HTML CSS JavaScript HTMX Tailwind CSS และ Daisy UI ในการออกแบบและตกแต่งหน้าเว็บ

<br>

## :gear: วิธีติดตั้งและรันโปรเจกต์

#### Requirements (ข้อกำหนดเบื้องต้น) :memo: 
ก่อนเริ่มติดตั้งโปรเจกต์นี้ กรุณาตรวจสอบว่าเครื่องของคุณมีเครื่องมือและซอฟต์แวร์ดังต่อไปนี้

**1. Python (เวอร์ชัน 3.8 ขึ้นไป)**
- ดาวน์โหลด: https://www.python.org/downloads/
- ตรวจสอบเวอร์ชัน:
  ```bash
  python --version
  ````

**2. Node.js**
>Tailwind CSS ใช้ Node.js และ npm สำหรับจัดการ frontend dependencies และคอมไพล์ CSS
- ดาวน์โหลด: https://nodejs.org/en/download
- ตรวจสอบเวอร์ชัน:

    ```bash
    node -v
    npm -v
    ```

**3. MySQL และ MySQL Workbench** 
>ขณะติดตั้งผ่าน MySQL Installer จะมีขั้นตอนให้ตั้งรหัสผ่านของผู้ใช้ `root` กรุณาจดหรือบันทึกรหัสผ่านนี้ไว้ เนื่องจากจำเป็นต้องใช้ในการเชื่อมต่อฐานข้อมูล
- ดาวน์โหลด MySQL Community Server (แนะนำเวอร์ชัน 8.0.42 ขึ้นไป): https://dev.mysql.com/downloads/mysql/
- ดาวน์โหลด MySQL Workbench: https://dev.mysql.com/downloads/workbench/

<br>

#### ขั้นตอนติดตั้ง :gear: 

**1. Clone โปรเจกต์จาก GitHub**

- ใช้คำสั่ง:

  ```bash
  gh repo clone nantiwan47/CNStyleShop
  ```

  หรือ

  ```bash
  git clone https://github.com/nantiwan47/CNStyleShop.git
  ```
- เข้าไปยังโฟลเดอร์โปรเจกต์

  ```bash
  cd CNStyleShop
  ```
<p align="center">
  <img src="https://github.com/user-attachments/assets/d32ba166-6585-4914-958f-976f74cc0b2b" alt="clone" width="500"/>
</p>

**2. สร้าง virtual environment และเปิดใช้งาน (สำหรับ Windows)**

  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
<p align="center">
  <img src="https://github.com/user-attachments/assets/52a67e0b-a8c0-4642-8f5a-75967081e7c1" alt="environment" width="500"/>
</p>

**3. ติดตั้ง Python dependencies**

  ```bash
  pip install -r requirements.txt
  ```
<p align="center">
  <img src="https://github.com/user-attachments/assets/91b2e5f6-d2db-476b-ae37-72a98185f02c" alt="install requirements" width="500"/>
</p>

**4. ติดตั้ง npm dependencies สำหรับ Tailwind CSS**

- เข้าไปยังโฟลเดอร์ที่เก็บไฟล์ frontend

  ```bash
  cd theme/static_src
  ```
- ติดตั้ง npm packages

  ```bash
  npm install
  ```
- กลับไปยังโฟลเดอร์โปรเจกต์หลัก
  ```bash
  cd ../../
  ```
  <p align="center">
    <img src="https://github.com/user-attachments/assets/3fc44555-60e6-4e84-b359-78a1c1f0a400" alt="npm" width="500"/>
  </p>

  >จากนั้นเปิดโปรเจกต์ด้วยโปรแกรมแก้ไขโค้ดที่สะดวก (เช่น VS Code, PyCharm ฯลฯ) หากใช้ VS Code สามารถใช้คำสั่ง: `code .`

**5. ตั้งค่า Database**

5.1 สร้าง Schema ชื่อ `cnstyleshop` ใน MySQL Workbench
>เปิด MySQL Workbench
>คลิกที่ Connection ที่ชื่อว่า Local instance MySQL (หรือชื่ออื่นที่คุณเคยตั้งไว้)
>ใส่รหัสผ่าน MySQL (ตั้งไว้ตอนติดตั้ง MySQL) เพื่อเข้าสู่หน้าหลัก

<p align="center">
    <img src="https://github.com/user-attachments/assets/6728de63-048e-41d3-b302-124e3d963b5d" alt="MySQL1" width="700"/>
</p>

>ที่แถบด้านซ้ายกดไอคอน Create a new Schema
>ตรงช่อง Name: ตั้งชื่อว่า **cnstyleshop** แล้วกด Apply
>จะมีหน้าต่าง SQL Preview ขึ้นมา กด Apply อีกครั้ง เมื่อเห็นข้อความ Success กด Finish

<p align="center">
  <img src="https://github.com/user-attachments/assets/f9d4e47f-43cc-47f8-94e8-df91f3e3287b" alt="MySQL1" width="700"/>
</p>

5.2 แก้ไขการเชื่อมต่อฐานข้อมูลใน Django
>ไปที่โปรเจกต์ Django (โฟลเดอร์ CNStyleShop) เปิดไฟล์ settings.py ไปที่ส่วน DATABASES และทำการแก้ไข USER และ PASSWORD ให้ตรงกับที่ตั้งไว้ตอนติดตั้ง MySQL

<p align="center">
  <img src="https://github.com/user-attachments/assets/181dd8d0-41ae-45d0-9938-171f6c260111" alt="MySQL1" width="700"/>
</p>

รันคำสั่ง migrate เพื่อสร้างตารางในฐานข้อมูล

  ```bash
  python manage.py migrate
  ```

> :warning: **ถ้าไม่มี MySQL ติดตั้งไว้**
> 
> สามารถใช้ SQLite แทนได้ง่ายๆ โดยแก้ไฟล์ `settings.py` บรรทัดที่ 113
> 
>     DATABASES['default'] = DATABASES['sqlite3']


**6. รัน Tailwind CSS**

  ```bash
  python manage.py tailwind start
  ```

<p align="center">
  <img src="https://github.com/user-attachments/assets/f806c3ed-7a3b-4be8-9877-8307ab2c46fe" alt="tailwind start" width="700"/>
</p>

**7. รัน Django**
>เปิดอีกหน้าต่างหนึ่งของ PowerShell หรือ Command Prompt แล้วรันคำสั่ง

  ```bash
  python manage.py runserver
  ```

<p align="center">
  <img src="https://github.com/user-attachments/assets/e595f001-52a8-4ecf-8437-4a2187223f67" alt="runserver" width="700"/>
</p>

---
<br>
เพิ่มเติม

**👤 สร้าง Superuser (สำหรับเข้าสู่ระบบ Django Admin)**
```bash
python manage.py createsuperuser
```

> ตัวอย่างข้อมูล: Username: `admin`, Email: `admin@gmail.com`, Password: `1234`
