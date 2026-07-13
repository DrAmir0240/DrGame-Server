# DrGame Database Seed Data — SQL INSERT Statements

> **Note:** Run these queries in order — foreign key dependencies are respected.
> All timestamps use `Asia/Tehran` timezone. IDs use PostgreSQL `DEFAULT` (auto-increment) unless specified.
> Passwords are hashed with Django's `pbkdf2_sha256` (the sample below is the hash for `"Test@1234"`).

---

## 1. `users_customuser`

```sql
-- Password hash = pbkdf2_sha256 hash of "Test@1234"
INSERT INTO users_customuser (id, password, last_login, phone, is_active, is_deleted, is_staff, is_superuser)
VALUES
  (1, 'pbkdf2_sha256$870000$salt$hash_placeholder_admin', NULL, '09120000001', TRUE, FALSE, TRUE, TRUE),
  (2, 'pbkdf2_sha256$870000$salt$hash_placeholder_emp1',  NULL, '09120000002', TRUE, FALSE, FALSE, FALSE),
  (3, 'pbkdf2_sha256$870000$salt$hash_placeholder_emp2',  NULL, '09120000003', TRUE, FALSE, FALSE, FALSE),
  (4, 'pbkdf2_sha256$870000$salt$hash_placeholder_cust1', NULL, '09120000004', TRUE, FALSE, FALSE, FALSE),
  (5, 'pbkdf2_sha256$870000$salt$hash_placeholder_cust2', NULL, '09120000005', TRUE, FALSE, FALSE, FALSE),
  (6, 'pbkdf2_sha256$870000$salt$hash_placeholder_repr1', NULL, '09120000006', TRUE, FALSE, FALSE, FALSE),
  (7, 'pbkdf2_sha256$870000$salt$hash_placeholder_hire1', NULL, '09120000007', TRUE, FALSE, FALSE, FALSE),
  (8, 'pbkdf2_sha256$870000$salt$hash_placeholder_blog',  NULL, '09120000008', TRUE, FALSE, FALSE, FALSE);

SELECT setval('users_customuser_id_seq', (SELECT MAX(id) FROM users_customuser));
```

---

## 2. `users_mainmanager`

```sql
INSERT INTO users_mainmanager (id, user_id, name, access, balance)
VALUES
  (1, 1, 'مدیر اصلی', '1', 50000000.00);
```

---

## 3. `users_otp`

```sql
INSERT INTO users_otp (id, user_id, code, created_at, expires_at)
VALUES
  (1, 4, '12345', NOW(), NOW() + INTERVAL '2 minutes'),
  (2, 5, '67890', NOW(), NOW() + INTERVAL '2 minutes');

SELECT setval('users_otp_id_seq', (SELECT MAX(id) FROM users_otp));
```

---

## 4. `users_apikey`

```sql
INSERT INTO users_apikey (id, key, client_name, is_active, created_at)
VALUES
  (1, 'sk-drgame-telegram-bot-key-sample-1234567890abcdef1234567890abcdef', 'Telegram Bot', TRUE, NOW()),
  (2, 'sk-drgame-website-key-sample-abcdef1234567890abcdef1234567890ab', 'Website Frontend', TRUE, NOW());

SELECT setval('users_apikey_id_seq', (SELECT MAX(id) FROM users_apikey));
```

---

## 5. `hr_employeerole`

```sql
INSERT INTO hr_employeerole (id, role_name, description,
    access_to_dashboard, can_read_task_manager, can_write_task_manager,
    can_read_accounting, can_write_accounting,
    can_read_inventory, can_write_inventory, access_to_all_inventory,
    can_read_orders, can_write_orders,
    can_read_account_orders, can_write_account_orders, access_to_all_accounts, is_account_employee,
    can_read_repairs, can_write_repairs,
    can_read_hr, can_write_hr,
    can_read_site, can_write_site,
    can_read_branch, can_write_branch,
    can_read_docs, can_write_docs,
    can_change_setting, access_to_messenger, can_start_chat)
VALUES
  (1, 'مدیر فروش', 'مدیر بخش فروش و سفارشات',
    TRUE, TRUE, TRUE,
    TRUE, FALSE,
    TRUE, TRUE, TRUE,
    TRUE, TRUE,
    TRUE, TRUE, TRUE, FALSE,
    FALSE, FALSE,
    FALSE, FALSE,
    TRUE, TRUE,
    FALSE, FALSE,
    FALSE, FALSE,
    FALSE, TRUE, TRUE),
  (2, 'حسابدار', 'مسئول مالی و حسابداری',
    TRUE, TRUE, FALSE,
    TRUE, TRUE,
    TRUE, FALSE, FALSE,
    TRUE, FALSE,
    FALSE, FALSE, FALSE, FALSE,
    FALSE, FALSE,
    FALSE, FALSE,
    FALSE, FALSE,
    FALSE, FALSE,
    TRUE, FALSE,
    FALSE, TRUE, FALSE),
  (3, 'انباردار', 'مسئول انبار و موجودی',
    TRUE, TRUE, FALSE,
    FALSE, FALSE,
    TRUE, TRUE, TRUE,
    FALSE, FALSE,
    FALSE, FALSE, FALSE, FALSE,
    FALSE, FALSE,
    FALSE, FALSE,
    FALSE, FALSE,
    FALSE, FALSE,
    FALSE, FALSE,
    FALSE, TRUE, FALSE),
  (4, 'تکنسین اکانت', 'مسئول اکانت‌های سونی',
    TRUE, TRUE, TRUE,
    FALSE, FALSE,
    TRUE, TRUE, FALSE,
    FALSE, FALSE,
    TRUE, TRUE, TRUE, TRUE,
    FALSE, FALSE,
    FALSE, FALSE,
    FALSE, FALSE,
    FALSE, FALSE,
    FALSE, FALSE,
    FALSE, TRUE, TRUE);

SELECT setval('hr_employeerole_id_seq', (SELECT MAX(id) FROM hr_employeerole));
```

---

## 6. `hr_employee`

```sql
INSERT INTO hr_employee (id, user_id, profile_picture, role_id, first_name, last_name,
    national_code, employee_id, balance, has_commission, commission_amount, is_deleted, created_at, updated_at)
VALUES
  (1, 2, NULL, 1, 'علی', 'احمدی', '0012345678', 'EMP001', 5000000, TRUE, 500000, FALSE, NOW(), NOW()),
  (2, 3, NULL, 4, 'رضا', 'محمدی', '0023456789', 'EMP002', 3000000, FALSE, 0, FALSE, NOW(), NOW());

SELECT setval('hr_employee_id_seq', (SELECT MAX(id) FROM hr_employee));
```

---

## 7. `hr_repairman`

```sql
INSERT INTO hr_repairman (id, user_id, profile_picture, first_name, last_name,
    national_code, balance, is_deleted, created_at, updated_at)
VALUES
  (1, 6, NULL, 'حسین', 'کریمی', '0034567890', 2000000, FALSE, NOW(), NOW());

SELECT setval('hr_repairman_id_seq', (SELECT MAX(id) FROM hr_repairman));
```

---

## 8. `hr_employeefile`

```sql
INSERT INTO hr_employeefile (id, employee_id, title, file, created_at, updated_at, is_deleted)
VALUES
  (1, 1, 'قرارداد کاری', 'employee_files/contract_ali.pdf', NOW(), NOW(), FALSE),
  (2, 2, 'مدرک تحصیلی', 'employee_files/degree_reza.pdf', NOW(), NOW(), FALSE);

SELECT setval('hr_employeefile_id_seq', (SELECT MAX(id) FROM hr_employeefile));
```

---

## 9. `hr_employeerequest`

```sql
INSERT INTO hr_employeerequest (id, employee_id, title, request_type, description, status, is_deleted, created_at, updated_at)
VALUES
  (1, 1, 'مرخصی تابستانی', 'leave', 'درخواست ۳ روز مرخصی استحقاقی', 'waiting', FALSE, NOW(), NOW()),
  (2, 2, 'مساعده حقوق', 'favorable', 'درخواست مساعده ۵ میلیون تومان', 'accepted', FALSE, NOW(), NOW());

SELECT setval('hr_employeerequest_id_seq', (SELECT MAX(id) FROM hr_employeerequest));
```

---

## 10. `hr_employeehire`

```sql
INSERT INTO hr_employeehire (id, full_name, birth_date, resume_file, phone_number, description, user_id, created_at)
VALUES
  (1, 'سارا رحیمی', '1375-06-15', 'hire/resume_files/sara_resume.pdf', '09120000007', 'متقاضی شغل فروشنده', 7, NOW());

SELECT setval('hr_employeehire_id_seq', (SELECT MAX(id) FROM hr_employeehire));
```

---

## 11. `crm_customer`

```sql
INSERT INTO crm_customer (id, full_name, user_id, address, postal_code, profile_pic,
    balance, is_business, discount, has_access_to_course, is_deleted, created_at, updated_at)
VALUES
  (1, 'محمد رضایی', 4, 'تهران، خیابان ولیعصر، پلاک ۱۲۳', '1234567890', NULL,
    1000000, FALSE, 5, FALSE, FALSE, NOW(), NOW()),
  (2, 'شرکت گیم‌نت', 5, 'اصفهان، خیابان چهارباغ، پلاک ۴۵', '5678901234', NULL,
    5000000, TRUE, 10, TRUE, FALSE, NOW(), NOW());

SELECT setval('crm_customer_id_seq', (SELECT MAX(id) FROM crm_customer));
```

---

## 12. `inventory_supplier`

```sql
INSERT INTO inventory_supplier (id, name, type, phone, email, address,
    account_number, sheba, national_id, tax_id, description,
    is_active, created_at, updated_at, is_deleted)
VALUES
  (1, 'تأمین‌کننده بازی ایران', 'legal', '02188001234', 'info@gamesupply.ir',
    'تهران، بازار موبایل', '1234567890', 'IR120000000000001234567890', '10320012345', '411234567890',
    'تأمین‌کننده اصلی بازی و لوازم', TRUE, NOW(), NOW(), FALSE),
  (2, 'محسن اکانت', 'real', '09351234567', NULL,
    'شیراز، پاساژ کوروش', NULL, NULL, '2345678901', NULL,
    'فروشنده اکانت سونی', TRUE, NOW(), NOW(), FALSE);

SELECT setval('inventory_supplier_id_seq', (SELECT MAX(id) FROM inventory_supplier));
```

---

## 13. `inventory_productcategory`

```sql
INSERT INTO inventory_productcategory (id, title, description, img, is_deleted, created_at, updated_at)
VALUES
  (1, 'کنسول بازی', 'انواع کنسول‌های بازی', NULL, FALSE, NOW(), NOW()),
  (2, 'لوازم جانبی', 'دسته، هدست و سایر لوازم', NULL, FALSE, NOW(), NOW()),
  (3, 'کارت اشتراک', 'کارت‌های PS Plus و اشتراک‌ها', NULL, FALSE, NOW(), NOW());

SELECT setval('inventory_productcategory_id_seq', (SELECT MAX(id) FROM inventory_productcategory));
```

---

## 14. `inventory_productcolor`

```sql
INSERT INTO inventory_productcolor (id, title, is_deleted, created_at, updated_at)
VALUES
  (1, 'سفید', FALSE, NOW(), NOW()),
  (2, 'مشکی', FALSE, NOW(), NOW()),
  (3, 'آبی', FALSE, NOW(), NOW());

SELECT setval('inventory_productcolor_id_seq', (SELECT MAX(id) FROM inventory_productcolor));
```

---

## 15. `inventory_productcompany`

```sql
INSERT INTO inventory_productcompany (id, title, is_deleted, created_at, updated_at)
VALUES
  (1, 'Sony', FALSE, NOW(), NOW()),
  (2, 'Microsoft', FALSE, NOW(), NOW()),
  (3, 'Nintendo', FALSE, NOW(), NOW());

SELECT setval('inventory_productcompany_id_seq', (SELECT MAX(id) FROM inventory_productcompany));
```

---

## 16. `inventory_product`

```sql
INSERT INTO inventory_product (id, title, main_img, description, color_id, category_id, company_id,
    price, stock, units_sold, is_deleted, created_at, updated_at)
VALUES
  (1, 'PlayStation 5 Slim', NULL, 'کنسول پلی استیشن ۵ اسلیم ۱ ترابایت',
    1, 1, 1, 28500000.00000, 15, 42, FALSE, NOW(), NOW()),
  (2, 'DualSense Controller', NULL, 'دسته بازی DualSense رنگ مشکی',
    2, 2, 1, 3200000.00000, 30, 85, FALSE, NOW(), NOW()),
  (3, 'Xbox Series X', NULL, 'کنسول ایکس باکس سری ایکس ۱ ترابایت',
    2, 1, 2, 26000000.00000, 8, 23, FALSE, NOW(), NOW()),
  (4, 'PS Plus 12 Month', NULL, 'اشتراک ۱۲ ماهه پلاس اسنشیال',
    1, 3, 1, 2400000.00000, 100, 156, FALSE, NOW(), NOW());

SELECT setval('inventory_product_id_seq', (SELECT MAX(id) FROM inventory_product));
```

---

## 17. `inventory_productimage`

```sql
INSERT INTO inventory_productimage (id, img, product_id, is_deleted, created_at, updated_at)
VALUES
  (1, 'images/products/ps5_side.jpg', 1, FALSE, NOW(), NOW()),
  (2, 'images/products/ps5_back.jpg', 1, FALSE, NOW(), NOW()),
  (3, 'images/products/dualsense_top.jpg', 2, FALSE, NOW(), NOW());

SELECT setval('inventory_productimage_id_seq', (SELECT MAX(id) FROM inventory_productimage));
```

---

## 18. `inventory_sonyaccountstatus`

```sql
INSERT INTO inventory_sonyaccountstatus (id, title, description, is_available, is_deleted, created_at, updated_at)
VALUES
  (1, 'فعال', 'اکانت فعال و آماده استفاده', TRUE, FALSE, NOW(), NOW()),
  (2, 'در حال تنظیم', 'در حال آماده‌سازی توسط تکنسین', TRUE, FALSE, NOW(), NOW()),
  (3, 'غیرفعال', 'اکانت معلق یا مسدود شده', FALSE, FALSE, NOW(), NOW()),
  (4, 'اجاره داده شده', 'اکانت فعلاً در اجاره مشتری', FALSE, FALSE, NOW(), NOW());

SELECT setval('inventory_sonyaccountstatus_id_seq', (SELECT MAX(id) FROM inventory_sonyaccountstatus));
```

---

## 19. `inventory_sonyaccountbank`

```sql
INSERT INTO inventory_sonyaccountbank (id, title, description, is_deleted, created_at, updated_at)
VALUES
  (1, 'بانک ملت', 'حساب بانک ملت برای خرید از استور', FALSE, NOW(), NOW()),
  (2, 'بانک سامان', 'حساب بانک سامان', FALSE, NOW(), NOW());

SELECT setval('inventory_sonyaccountbank_id_seq', (SELECT MAX(id) FROM inventory_sonyaccountbank));
```

---

## 20. `inventory_game`

```sql
INSERT INTO inventory_game (id, title, main_img, volume, 
    online_ps4_price, online_ps5_price, offline_ps4_price, offline_ps5_price,
    data_ps4_price, data_ps5_price, xbox_price, nintendo_price,
    description, is_trend, units_sold, is_deleted, created_at, updated_at)
VALUES
  (1, 'God of War Ragnarök', NULL, 80,
    250000, 300000, 150000, 200000,
    100000, 120000, NULL, NULL,
    'بازی گاد آو وار رگناروک', TRUE, 320, FALSE, NOW(), NOW()),
  (2, 'FIFA 25', NULL, 50,
    200000, 250000, 120000, 150000,
    80000, 100000, 200000, NULL,
    'بازی فیفا ۲۵', TRUE, 580, FALSE, NOW(), NOW()),
  (3, 'Spider-Man 2', NULL, 65,
    280000, 320000, 170000, 210000,
    110000, 130000, NULL, NULL,
    'بازی اسپایدرمن ۲', TRUE, 245, FALSE, NOW(), NOW()),
  (4, 'The Last of Us Part II', NULL, 75,
    220000, 270000, 140000, 180000,
    90000, 110000, NULL, NULL,
    'بازی لست آو آس پارت ۲', TRUE, 410, FALSE, NOW(), NOW()),
  (5, 'Zelda: Tears of the Kingdom', NULL, 16,
    NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, 350000,
    'بازی زلدا: اشک‌های پادشاهی', FALSE, 95, FALSE, NOW(), NOW());

SELECT setval('inventory_game_id_seq', (SELECT MAX(id) FROM inventory_game));
```

---

## 21. `inventory_gameimage`

```sql
INSERT INTO inventory_gameimage (id, img, game_id, is_deleted, created_at, updated_at)
VALUES
  (1, 'images/games/gow_ragnarok_1.jpg', 1, FALSE, NOW(), NOW()),
  (2, 'images/games/fifa25_cover.jpg', 2, FALSE, NOW(), NOW()),
  (3, 'images/games/spiderman2_1.jpg', 3, FALSE, NOW(), NOW());

SELECT setval('inventory_gameimage_id_seq', (SELECT MAX(id) FROM inventory_gameimage));
```

---

## 22. `inventory_sonyaccount`

```sql
INSERT INTO inventory_sonyaccount (id, username, password, employee_id, two_step,
    status_id, bank_account_status, bank_account_id, plus,
    region, is_sold, is_owned, is_deleted, created_at, updated_at,
    two_step_secret, two_step_enabled)
VALUES
  (1, 'drgame_acc_01@gmail.com', 'P@ssw0rd_Sony1', 2, NULL,
    1, TRUE, 1, TRUE,
    'America', FALSE, TRUE, FALSE, NOW(), NOW(),
    NULL, FALSE),
  (2, 'drgame_acc_02@gmail.com', 'P@ssw0rd_Sony2', 2, NULL,
    1, TRUE, 2, TRUE,
    'Europe', FALSE, TRUE, FALSE, NOW(), NOW(),
    NULL, FALSE),
  (3, 'drgame_acc_03@gmail.com', 'P@ssw0rd_Sony3', NULL, NULL,
    4, FALSE, NULL, FALSE,
    'Asia', FALSE, FALSE, FALSE, NOW(), NOW(),
    NULL, FALSE),
  (4, 'sold_acc_01@gmail.com', 'P@ssw0rd_Sold1', NULL, NULL,
    3, FALSE, NULL, FALSE,
    'America', TRUE, FALSE, FALSE, NOW(), NOW(),
    NULL, FALSE);

SELECT setval('inventory_sonyaccount_id_seq', (SELECT MAX(id) FROM inventory_sonyaccount));
```

---

## 23. `inventory_sonyaccountgame` (M2M through table)

```sql
INSERT INTO inventory_sonyaccountgame (id, sony_account_id, game_id, is_deleted, created_at, updated_at)
VALUES
  (1, 1, 1, FALSE, NOW(), NOW()),
  (2, 1, 2, FALSE, NOW(), NOW()),
  (3, 1, 3, FALSE, NOW(), NOW()),
  (4, 2, 2, FALSE, NOW(), NOW()),
  (5, 2, 4, FALSE, NOW(), NOW()),
  (6, 3, 1, FALSE, NOW(), NOW());

SELECT setval('inventory_sonyaccountgame_id_seq', (SELECT MAX(id) FROM inventory_sonyaccountgame));
```

---

## 24. `inventory_doccategory`

```sql
INSERT INTO inventory_doccategory (id, title, description, is_deleted, created_at, updated_at)
VALUES
  (1, 'فاکتورها', 'اسناد مربوط به فاکتور خرید و فروش', FALSE, NOW(), NOW()),
  (2, 'قراردادها', 'قراردادهای همکاری و تأمین', FALSE, NOW(), NOW());

SELECT setval('inventory_doccategory_id_seq', (SELECT MAX(id) FROM inventory_doccategory));
```

---

## 25. `inventory_docsubcategory`

```sql
INSERT INTO inventory_docsubcategory (id, title, description, category_id, is_deleted, created_at, updated_at)
VALUES
  (1, 'فاکتور خرید', 'فاکتورهای خرید از تأمین‌کنندگان', 1, FALSE, NOW(), NOW()),
  (2, 'فاکتور فروش', 'فاکتورهای فروش به مشتریان', 1, FALSE, NOW(), NOW()),
  (3, 'قرارداد همکاری', 'قراردادهای همکاری با تأمین‌کنندگان', 2, FALSE, NOW(), NOW());

SELECT setval('inventory_docsubcategory_id_seq', (SELECT MAX(id) FROM inventory_docsubcategory));
```

---

## 26. `inventory_document`

```sql
INSERT INTO inventory_document (id, title, file, category_id, is_deleted, created_at, updated_at)
VALUES
  (1, 'فاکتور خرید PS5 - تیر ۱۴۰۵', 'docs/invoice_ps5_tir1405.pdf', 1, FALSE, NOW(), NOW()),
  (2, 'قرارداد همکاری بازی ایران', 'docs/contract_gamesupply.pdf', 3, FALSE, NOW(), NOW());

SELECT setval('inventory_document_id_seq', (SELECT MAX(id) FROM inventory_document));
```

---

## 27. `inventory_realassetscategory`

```sql
INSERT INTO inventory_realassetscategory (id, title, description, is_deleted, created_at, updated_at)
VALUES
  (1, 'تجهیزات فروشگاه', 'میز، صندلی، قفسه و دکور', FALSE, NOW(), NOW()),
  (2, 'تجهیزات IT', 'کامپیوتر، مانیتور، سرور', FALSE, NOW(), NOW());

SELECT setval('inventory_realassetscategory_id_seq', (SELECT MAX(id) FROM inventory_realassetscategory));
```

---

## 28. `inventory_realassetssubcategory`

```sql
INSERT INTO inventory_realassetssubcategory (id, title, description, category_id, is_deleted, created_at, updated_at)
VALUES
  (1, 'مانیتور', 'مانیتورهای فروشگاه', 2, FALSE, NOW(), NOW()),
  (2, 'قفسه نمایش', 'قفسه‌های نمایش محصولات', 1, FALSE, NOW(), NOW());

SELECT setval('inventory_realassetssubcategory_id_seq', (SELECT MAX(id) FROM inventory_realassetssubcategory));
```

---

## 29. `inventory_realassets`

```sql
INSERT INTO inventory_realassets (id, title, image, category_id, employee_id, price, is_deleted, created_at, updated_at)
VALUES
  (1, 'مانیتور سامسونگ ۲۷ اینچ', NULL, 1, 1, 12000000, FALSE, NOW(), NOW()),
  (2, 'قفسه نمایش شیشه‌ای', NULL, 2, NULL, 8000000, FALSE, NOW(), NOW());

SELECT setval('inventory_realassets_id_seq', (SELECT MAX(id) FROM inventory_realassets));
```

---

## 30. `accounting_bankaccount`

```sql
INSERT INTO accounting_bankaccount (id, title, account_number, sheba, description, created_at, updated_at, is_deleted)
VALUES
  (1, 'حساب اصلی ملت', '6104337812345678', 'IR120560611028001234567890', 'حساب اصلی فروشگاه', NOW(), NOW(), FALSE),
  (2, 'حساب سپهر', '5892101234567890', 'IR450170000000201234567890', 'حساب دوم فروشگاه', NOW(), NOW(), FALSE);

SELECT setval('accounting_bankaccount_id_seq', (SELECT MAX(id) FROM accounting_bankaccount));
```

---

## 31. `accounting_accountside`

```sql
-- ContentType IDs depend on your DB. Use a subquery to find them dynamically.
INSERT INTO accounting_accountside (id, name, type, content_type_id, object_id, created_at, updated_at, is_deleted)
VALUES
  (1, 'محمد رضایی', 'customer',
    (SELECT id FROM django_content_type WHERE app_label='crm' AND model='customer'), 1,
    NOW(), NOW(), FALSE),
  (2, 'شرکت گیم‌نت', 'customer',
    (SELECT id FROM django_content_type WHERE app_label='crm' AND model='customer'), 2,
    NOW(), NOW(), FALSE),
  (3, 'علی احمدی', 'employee',
    (SELECT id FROM django_content_type WHERE app_label='hr' AND model='employee'), 1,
    NOW(), NOW(), FALSE),
  (4, 'تأمین‌کننده بازی ایران', 'supplier',
    (SELECT id FROM django_content_type WHERE app_label='inventory' AND model='supplier'), 1,
    NOW(), NOW(), FALSE),
  (5, 'متفرقه', 'other', NULL, NULL, NOW(), NOW(), FALSE);

SELECT setval('accounting_accountside_id_seq', (SELECT MAX(id) FROM accounting_accountside));
```

---

## 32. `accounting_invoicecategory`

```sql
INSERT INTO accounting_invoicecategory (id, title, direction, description, created_at, updated_at, is_deleted)
VALUES
  (1, 'فروش محصول', 'in', 'درآمد حاصل از فروش محصولات', NOW(), NOW(), FALSE),
  (2, 'فروش اکانت', 'in', 'درآمد حاصل از فروش و اجاره اکانت', NOW(), NOW(), FALSE),
  (3, 'خرید از تأمین‌کننده', 'out', 'خرید کالا از تأمین‌کنندگان', NOW(), NOW(), FALSE),
  (4, 'تعمیرات', 'in', 'درآمد از تعمیر دستگاه‌ها', NOW(), NOW(), FALSE),
  (5, 'حقوق و دستمزد', 'out', 'پرداخت حقوق کارکنان', NOW(), NOW(), FALSE);

SELECT setval('accounting_invoicecategory_id_seq', (SELECT MAX(id) FROM accounting_invoicecategory));
```

---

## 33. `accounting_invoice`

```sql
INSERT INTO accounting_invoice (id, account_side_id, category_id, discount, amount, paid_amount,
    status, payment_status, is_payroll, description, created_at, updated_at, is_deleted)
VALUES
  (1, 1, 1, 0, 28500000, 28500000, 'finalize', 'paid', FALSE,
    'فروش PS5 به محمد رضایی', NOW(), NOW(), FALSE),
  (2, 2, 2, 500000, 1200000, 700000, 'primary', 'partial', FALSE,
    'اجاره اکانت به شرکت گیم‌نت', NOW(), NOW(), FALSE),
  (3, 4, 3, 0, 150000000, 150000000, 'finalize', 'paid', FALSE,
    'خرید محموله PS5 از تأمین‌کننده', NOW(), NOW(), FALSE),
  (4, 3, 5, 0, 25000000, 25000000, 'finalize', 'paid', TRUE,
    'حقوق تیر ماه - علی احمدی', NOW(), NOW(), FALSE);

SELECT setval('accounting_invoice_id_seq', (SELECT MAX(id) FROM accounting_invoice));
```

---

## 34. `accounting_invoiceitem`

```sql
INSERT INTO accounting_invoiceitem (id, invoice_id, title, quantity, unit_price, discount,
    content_type_id, object_id, created_at, updated_at, is_deleted)
VALUES
  (1, 1, 'PlayStation 5 Slim', 1, 28500000, 0,
    (SELECT id FROM django_content_type WHERE app_label='inventory' AND model='product'), 1,
    NOW(), NOW(), FALSE),
  (2, 2, 'اجاره اکانت GOW Ragnarok', 1, 600000, 0,
    (SELECT id FROM django_content_type WHERE app_label='inventory' AND model='sonyaccount'), 1,
    NOW(), NOW(), FALSE),
  (3, 2, 'اجاره اکانت FIFA 25', 1, 600000, 0,
    (SELECT id FROM django_content_type WHERE app_label='inventory' AND model='sonyaccount'), 2,
    NOW(), NOW(), FALSE),
  (4, 3, 'خرید عمده PS5 Slim', 5, 27000000, 0, NULL, NULL, NOW(), NOW(), FALSE),
  (5, 3, 'خرید عمده DualSense', 10, 1500000, 0, NULL, NULL, NOW(), NOW(), FALSE);

SELECT setval('accounting_invoiceitem_id_seq', (SELECT MAX(id) FROM accounting_invoiceitem));
```

---

## 35. `accounting_payrolldetail`

```sql
INSERT INTO accounting_payrolldetail (id, invoice_id, base_salary, overtime_amount, bonus,
    housing_allowance, food_allowance, transportation_allowance,
    insurance_deduction, tax_deduction, loan_deduction, other_deductions,
    work_days, overtime_hours, description, created_at, updated_at)
VALUES
  (1, 4, 18000000, 3000000, 2000000,
    3000000, 1500000, 1000000,
    2000000, 500000, 1000000, 0,
    26, 15, 'حقوق تیر ماه ۱۴۰۵ - علی احمدی', NOW(), NOW());

SELECT setval('accounting_payrolldetail_id_seq', (SELECT MAX(id) FROM accounting_payrolldetail));
```

---

## 36. `accounting_transaction`

```sql
INSERT INTO accounting_transaction (id, invoice_id, account_side_id, bank_account_id,
    amount, direction, description, created_at, updated_at, is_deleted)
VALUES
  (1, 1, 1, 1, 28500000, 'in', 'دریافت وجه فروش PS5', NOW(), NOW(), FALSE),
  (2, 2, 2, 1, 700000, 'in', 'دریافت بخشی از وجه اجاره اکانت', NOW(), NOW(), FALSE),
  (3, 3, 4, 1, 150000000, 'out', 'پرداخت به تأمین‌کننده', NOW(), NOW(), FALSE),
  (4, 4, 3, 2, 25000000, 'out', 'پرداخت حقوق علی احمدی', NOW(), NOW(), FALSE);

SELECT setval('accounting_transaction_id_seq', (SELECT MAX(id) FROM accounting_transaction));
```

---

## 37. `task_manager_plannedtask`

```sql
INSERT INTO task_manager_plannedtask (id, employee_id, title, voice, type, description, status,
    priority, has_reward, reward_amount, approved, start_date, deadline,
    is_deleted, created_at, updated_at)
VALUES
  (1, 1, 'به‌روزرسانی قیمت‌ها', NULL, 'Organize', 'آپدیت قیمت تمام محصولات در سیستم',
    'in_progress', 'high', FALSE, NULL, FALSE,
    NOW(), NOW() + INTERVAL '3 days', FALSE, NOW(), NOW()),
  (2, 2, 'تنظیم اکانت‌های جدید', NULL, 'Organize', 'تنظیم و آماده‌سازی ۱۰ اکانت جدید سونی',
    'planed', 'immediate', TRUE, 500000, FALSE,
    NOW() + INTERVAL '1 day', NOW() + INTERVAL '5 days', FALSE, NOW(), NOW()),
  (3, 1, 'شمارش موجودی انبار', NULL, 'Organize', 'شمارش فیزیکی تمام موجودی انبار',
    'done', 'medium', TRUE, 300000, TRUE,
    NOW() - INTERVAL '5 days', NOW() - INTERVAL '2 days', FALSE, NOW(), NOW());

SELECT setval('task_manager_plannedtask_id_seq', (SELECT MAX(id) FROM task_manager_plannedtask));
```

---

## 38. `task_manager_dailytask`

```sql
INSERT INTO task_manager_dailytask (id, title, type, description, is_deleted, created_at, updated_at)
VALUES
  (1, 'بررسی سفارشات روز', 'Organize', 'بررسی و پیگیری تمام سفارشات ورودی روز', FALSE, NOW(), NOW()),
  (2, 'پشتیبانی تلگرام', 'Organize', 'پاسخگویی به پیام‌های مشتریان در تلگرام', FALSE, NOW(), NOW());

SELECT setval('task_manager_dailytask_id_seq', (SELECT MAX(id) FROM task_manager_dailytask));
```

---

## 39. `task_manager_dailytask_employees` (M2M auto table)

```sql
INSERT INTO task_manager_dailytask_employees (id, dailytask_id, employee_id)
VALUES
  (1, 1, 1),
  (2, 1, 2),
  (3, 2, 1);

SELECT setval('task_manager_dailytask_employees_id_seq', (SELECT MAX(id) FROM task_manager_dailytask_employees));
```

---

## 40. `messenger_chatroom`

```sql
INSERT INTO messenger_chatroom (id, name, type, owner_id, created_at)
VALUES
  (1, '', 'pv', 2, NOW()),
  (2, 'گروه فروش', 'group', 2, NOW()),
  (3, 'کانال اطلاع‌رسانی', 'channel', 1, NOW());

SELECT setval('messenger_chatroom_id_seq', (SELECT MAX(id) FROM messenger_chatroom));
```

---

## 41. `messenger_membership`

```sql
INSERT INTO messenger_membership (id, user_id, chat_room_id, is_admin, is_muted, joined_at)
VALUES
  (1, 2, 1, FALSE, FALSE, NOW()),
  (2, 3, 1, FALSE, FALSE, NOW()),
  (3, 2, 2, TRUE, FALSE, NOW()),
  (4, 3, 2, FALSE, FALSE, NOW()),
  (5, 1, 3, TRUE, FALSE, NOW()),
  (6, 2, 3, FALSE, FALSE, NOW()),
  (7, 3, 3, FALSE, FALSE, NOW());

SELECT setval('messenger_membership_id_seq', (SELECT MAX(id) FROM messenger_membership));
```

---

## 42. `messenger_message`

```sql
INSERT INTO messenger_message (id, room_id, sender_id, text, reply_to_id, created_at, is_edited, is_deleted)
VALUES
  (1, 1, 2, 'سلام رضا، اکانت‌ها آماده شدن؟', NULL, NOW() - INTERVAL '1 hour', FALSE, FALSE),
  (2, 1, 3, 'سلام، بله ۵ تاشون ردیفه', 1, NOW() - INTERVAL '55 minutes', FALSE, FALSE),
  (3, 2, 2, 'بچه‌ها قیمت PS5 عوض شده، آپدیت کنید', NULL, NOW() - INTERVAL '30 minutes', FALSE, FALSE),
  (4, 3, 1, 'اطلاعیه: ساعت کاری فردا ۱۰ صبح شروع میشه', NULL, NOW() - INTERVAL '2 hours', FALSE, FALSE);

SELECT setval('messenger_message_id_seq', (SELECT MAX(id) FROM messenger_message));
```

---

## 43. `orders_productorderstage`

```sql
INSERT INTO orders_productorderstage (id, title, is_in_progress, is_in_waiting, employee_role_id,
    description, created_at, updated_at, is_deleted)
VALUES
  (1, 'ثبت سفارش', FALSE, TRUE, 1, 'سفارش ثبت شده و در انتظار بررسی', NOW(), NOW(), FALSE),
  (2, 'آماده‌سازی', TRUE, FALSE, 3, 'در حال آماده‌سازی از انبار', NOW(), NOW(), FALSE),
  (3, 'ارسال شده', FALSE, FALSE, 1, 'سفارش ارسال شده', NOW(), NOW(), FALSE);

SELECT setval('orders_productorderstage_id_seq', (SELECT MAX(id) FROM orders_productorderstage));
```

---

## 44. `orders_productorder`

```sql
INSERT INTO orders_productorder (id, customer_id, invoice_id, stage_id, description,
    amount, created_at, updated_at, is_deleted)
VALUES
  (1, 1, 1, 3, 'سفارش PS5 برای محمد رضایی', 28500000, NOW(), NOW(), FALSE),
  (2, 2, NULL, 1, 'سفارش عمده لوازم جانبی', 15000000, NOW(), NOW(), FALSE);

SELECT setval('orders_productorder_id_seq', (SELECT MAX(id) FROM orders_productorder));
```

---

## 45. `orders_productorderitem`

```sql
INSERT INTO orders_productorderitem (id, product_order_id, title, quantity, unit_price, amount,
    created_at, updated_at, is_deleted)
VALUES
  (1, 1, 'PlayStation 5 Slim', 1, 28500000, 28500000, NOW(), NOW(), FALSE),
  (2, 2, 'DualSense Controller مشکی', 3, 3200000, 9600000, NOW(), NOW(), FALSE),
  (3, 2, 'PS Plus 12 Month', 2, 2400000, 4800000, NOW(), NOW(), FALSE);

SELECT setval('orders_productorderitem_id_seq', (SELECT MAX(id) FROM orders_productorderitem));
```

---

## 46. `orders_repairorderstage`

```sql
INSERT INTO orders_repairorderstage (id, title, is_in_progress, is_in_waiting, employee_role_id,
    description, created_at, updated_at, is_deleted)
VALUES
  (1, 'پذیرش', FALSE, TRUE, 1, 'دستگاه پذیرش شده', NOW(), NOW(), FALSE),
  (2, 'در حال تعمیر', TRUE, FALSE, 1, 'تکنسین در حال تعمیر', NOW(), NOW(), FALSE),
  (3, 'آماده تحویل', FALSE, FALSE, 1, 'تعمیر انجام شده و آماده تحویل', NOW(), NOW(), FALSE);

SELECT setval('orders_repairorderstage_id_seq', (SELECT MAX(id) FROM orders_repairorderstage));
```

---

## 47. `orders_repairordercategory`

```sql
INSERT INTO orders_repairordercategory (id, title, description, is_active, created_at, updated_at, is_deleted)
VALUES
  (1, 'تعمیر کنسول', 'تعمیرات انواع کنسول‌های بازی', TRUE, NOW(), NOW(), FALSE),
  (2, 'تعمیر دسته', 'تعمیر انواع دسته‌های بازی', TRUE, NOW(), NOW(), FALSE),
  (3, 'تعمیر هارد', 'تعمیر و تعویض هارد دیسک', TRUE, NOW(), NOW(), FALSE);

SELECT setval('orders_repairordercategory_id_seq', (SELECT MAX(id) FROM orders_repairordercategory));
```

---

## 48. `orders_repairorder`

```sql
INSERT INTO orders_repairorder (id, customer_id, invoice_id, stage_id, category_id,
    repair_fee, final_amount, created_at, updated_at, is_deleted)
VALUES
  (1, 1, NULL, 2, 1, 3500000, 4000000, NOW(), NOW(), FALSE),
  (2, 2, NULL, 3, 2, 1500000, 1800000, NOW(), NOW(), FALSE);

SELECT setval('orders_repairorder_id_seq', (SELECT MAX(id) FROM orders_repairorder));
```

---

## 49. `orders_repairorderdevice`

```sql
INSERT INTO orders_repairorderdevice (id, customer_id, repair_order_id, title,
    serial_number, created_at, updated_at, is_deleted)
VALUES
  (1, 1, 1, 'PlayStation 5', 'CFI-1215A-SN12345', NOW(), NOW(), FALSE),
  (2, 2, 2, 'DualSense Controller', 'DS-SN67890', NOW(), NOW(), FALSE);

SELECT setval('orders_repairorderdevice_id_seq', (SELECT MAX(id) FROM orders_repairorderdevice));
```

---

## 50. `orders_sonyaccountorderstage`

```sql
INSERT INTO orders_sonyaccountorderstage (id, title, is_in_progress, is_in_waiting, employee_role_id,
    description, created_at, updated_at, is_deleted)
VALUES
  (1, 'ثبت درخواست', FALSE, TRUE, 4, 'درخواست ثبت شده و در انتظار تکنسین', NOW(), NOW(), FALSE),
  (2, 'در حال تنظیم', TRUE, FALSE, 4, 'تکنسین در حال تنظیم اکانت', NOW(), NOW(), FALSE),
  (3, 'تحویل داده شده', FALSE, FALSE, 4, 'اکانت تحویل مشتری شد', NOW(), NOW(), FALSE);

SELECT setval('orders_sonyaccountorderstage_id_seq', (SELECT MAX(id) FROM orders_sonyaccountorderstage));
```

---

## 51. `orders_sonyaccountordercategory`

```sql
INSERT INTO orders_sonyaccountordercategory (id, title, type, rent_time_days, account_capacity)
VALUES
  (1, 'خرید اکانت آفلاین', 'buy', NULL, '1'),
  (2, 'اجاره اکانت آنلاین ۳۰ روزه', 'rent', 30, '2'),
  (3, 'اجاره اکانت آنلاین ۹۰ روزه', 'rent', 90, '2'),
  (4, 'خرید اکانت آنلاین', 'buy', NULL, '3');

SELECT setval('orders_sonyaccountordercategory_id_seq', (SELECT MAX(id) FROM orders_sonyaccountordercategory));
```

---

## 52. `orders_sonyaccountorder`

```sql
INSERT INTO orders_sonyaccountorder (id, customer_id, invoice_id, stage_id, category_id,
    source, type, amount, created_at, updated_at, is_deleted)
VALUES
  (1, 1, 2, 3, 2, 'telegram', 'by_customer', 600000, NOW(), NOW(), FALSE),
  (2, 2, NULL, 1, 1, 'website', 'by_employee', 300000, NOW(), NOW(), FALSE);

SELECT setval('orders_sonyaccountorder_id_seq', (SELECT MAX(id) FROM orders_sonyaccountorder));
```

---

## 53. `orders_sonyaccountorderconsole`

```sql
INSERT INTO orders_sonyaccountorderconsole (id, customer_id, sony_account_order_id,
    serial_number, created_at, updated_at, is_deleted)
VALUES
  (1, 1, 1, 'PS5-SN-ABCDEF123', NOW(), NOW(), FALSE),
  (2, 2, 2, 'PS4-SN-GHIJKL456', NOW(), NOW(), FALSE);

SELECT setval('orders_sonyaccountorderconsole_id_seq', (SELECT MAX(id) FROM orders_sonyaccountorderconsole));
```

---

## 54. `orders_sonyaccountorderitem`

```sql
INSERT INTO orders_sonyaccountorderitem (id, sony_account_order_id, sony_account_id, employee_id,
    created_at, updated_at)
VALUES
  (1, 1, 1, 2, NOW(), NOW()),
  (2, 2, 3, NULL, NOW(), NOW());

SELECT setval('orders_sonyaccountorderitem_id_seq', (SELECT MAX(id) FROM orders_sonyaccountorderitem));
```

---

## 55. `website_cart`

```sql
INSERT INTO website_cart (id, user_id, created_at, is_deleted)
VALUES
  ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1, NOW(), FALSE),
  ('b2c3d4e5-f6a7-8901-bcde-f12345678901', 2, NOW(), FALSE);
```

---

## 56. `website_cartitem`

```sql
INSERT INTO website_cartitem (id, cart_id, product_id, quantity, is_deleted, created_at, updated_at)
VALUES
  (1, 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 2, 1, FALSE, NOW(), NOW()),
  (2, 'b2c3d4e5-f6a7-8901-bcde-f12345678901', 4, 3, FALSE, NOW(), NOW());

SELECT setval('website_cartitem_id_seq', (SELECT MAX(id) FROM website_cartitem));
```

---

## 57. `website_gamecart`

```sql
INSERT INTO website_gamecart (id, user_id, type, price, created_at, updated_at, is_deleted)
VALUES
  (1, 1, 'online_ps5', 300000, NOW(), NOW(), FALSE),
  (2, 2, 'offline_ps4', 150000, NOW(), NOW(), FALSE);

SELECT setval('website_gamecart_id_seq', (SELECT MAX(id) FROM website_gamecart));
```

---

## 58. `website_gamecartitem`

```sql
INSERT INTO website_gamecartitem (id, game_cart_id, game_id, price, created_at, updated_at)
VALUES
  (1, 1, 1, 300000, NOW(), NOW()),
  (2, 1, 3, 320000, NOW(), NOW()),
  (3, 2, 2, 120000, NOW(), NOW());

SELECT setval('website_gamecartitem_id_seq', (SELECT MAX(id) FROM website_gamecartitem));
```

---

## 59. `website_blogpost`

```sql
INSERT INTO website_blogpost (id, title, slug, author_id, content, featured_image,
    meta_description, status, is_deleted, created_at, updated_at, published_at)
VALUES
  (1, 'بررسی PlayStation 5 Pro', 'بررسی-playstation-5-pro', 8,
    'در این مقاله به بررسی جامع کنسول جدید پلی‌استیشن ۵ پرو می‌پردازیم. این کنسول با قدرت پردازشی بالاتر و قابلیت ری‌تریسینگ بهبودیافته عرضه شده است...',
    NULL, 'بررسی کامل PS5 Pro با مشخصات فنی و مقایسه', 'published', FALSE, NOW(), NOW(), NOW()),
  (2, 'بهترین بازی‌های ۲۰۲۶', 'بهترین-بازیهای-2026', 8,
    'لیست بهترین بازی‌های سال ۲۰۲۶ برای پلتفرم‌های مختلف...',
    NULL, 'معرفی بهترین بازی‌های سال ۲۰۲۶', 'draft', FALSE, NOW(), NOW(), NOW());

SELECT setval('website_blogpost_id_seq', (SELECT MAX(id) FROM website_blogpost));
```

---

## 60. `website_aboutus`

```sql
INSERT INTO website_aboutus (id, title, subtitle, content, banner_image, team_image,
    is_deleted, created_at, updated_at)
VALUES
  (1, 'درباره دکتر گیم', 'فروشگاه تخصصی بازی و کنسول',
    'فروشگاه دکتر گیم از سال ۱۳۹۸ فعالیت خود را در زمینه فروش و اجاره بازی‌های دیجیتال، کنسول‌های بازی و لوازم جانبی آغاز کرده است. ما با تیمی حرفه‌ای و متعهد، بهترین خدمات را به گیمرهای عزیز ارائه می‌دهیم.',
    NULL, NULL, FALSE, NOW(), NOW());

SELECT setval('website_aboutus_id_seq', (SELECT MAX(id) FROM website_aboutus));
```

---

## 61. `website_contactus`

```sql
INSERT INTO website_contactus (id, address, phone, email, map_embed_code, opening_hours,
    facebook_url, twitter_url, instagram_url, is_deleted, created_at, updated_at)
VALUES
  (1, 'تهران، میدان ونک، خیابان شیراز شمالی، پلاک ۴۵', '02188776655', 'info@gamedr.ir',
    '<iframe src="https://maps.google.com/maps?q=35.7575,51.4100&output=embed"></iframe>',
    '10:00 - 22:00',
    '', '', 'https://instagram.com/gamedr.ir',
    FALSE, NOW(), NOW());

SELECT setval('website_contactus_id_seq', (SELECT MAX(id) FROM website_contactus));
```

---

## 62. `website_contactsubmission`

```sql
INSERT INTO website_contactsubmission (id, user_id, name, email, phone, subject, message,
    is_deleted, created_at, updated_at)
VALUES
  (1, 4, 'محمد رضایی', 'mohammad@email.com', '09120000004', 'سوال درباره اکانت',
    'سلام، من اکانتی رو اجاره کردم ولی هنوز تحویل نگرفتم. لطفاً پیگیری کنید.',
    FALSE, NOW(), NOW()),
  (2, 5, 'شرکت گیم‌نت', 'info@gamenet.ir', '09120000005', 'همکاری تجاری',
    'سلام، ما یک شرکت بازی هستیم و مایل به همکاری عمده هستیم.',
    FALSE, NOW(), NOW());

SELECT setval('website_contactsubmission_id_seq', (SELECT MAX(id) FROM website_contactsubmission));
```

---

## 63. `website_course`

```sql
INSERT INTO website_course (id, title, slug, description, course_image, price, status, created_at, updated_at)
VALUES
  (1, 'آموزش تنظیم اکانت PS', 'آموزش-تنظیم-اکانت-ps', 
    'دوره آموزشی کامل نحوه ساخت و تنظیم اکانت PlayStation با آموزش فعال‌سازی دو مرحله‌ای و خرید از استور',
    'course/ps_account_course.jpg', 250000.00, 'published', NOW(), NOW()),
  (2, 'آموزش تعمیر دسته بازی', 'آموزش-تعمیر-دسته-بازی',
    'آموزش تعمیرات پایه دسته‌های DualSense و DualShock',
    'course/controller_repair.jpg', 180000.00, 'draft', NOW(), NOW());

SELECT setval('website_course_id_seq', (SELECT MAX(id) FROM website_course));
```

---

## 64. `website_video`

```sql
INSERT INTO website_video (id, title, slug, description, video_file, status,
    course_id, duration, priority, created_at, updated_at)
VALUES
  (1, 'ساخت اکانت PSN', 'ساخت-اکانت-psn',
    'آموزش گام به گام ساخت اکانت PSN آمریکا',
    'videos/create_psn_account.mp4', 'published',
    1, '00:15:30', 1, NOW(), NOW()),
  (2, 'فعال‌سازی 2FA', 'فعالسازی-2fa',
    'آموزش فعال‌سازی احراز هویت دو مرحله‌ای',
    'videos/enable_2fa.mp4', 'published',
    1, '00:08:45', 2, NOW(), NOW()),
  (3, 'خرید از PS Store', 'خرید-از-ps-store',
    'آموزش خرید بازی از فروشگاه PlayStation',
    'videos/buy_from_store.mp4', 'draft',
    1, '00:12:00', 3, NOW(), NOW());

SELECT setval('website_video_id_seq', (SELECT MAX(id) FROM website_video));
```

---

## 65. `website_homebanner`

```sql
INSERT INTO website_homebanner (id, title, image, is_chosen, "order", created_at, updated_at)
VALUES
  (1, 'فروش ویژه PS5', 'banners/ps5_sale.jpg', TRUE, 1, NOW(), NOW()),
  (2, 'اجاره اکانت بازی', 'banners/account_rent.jpg', TRUE, 2, NOW(), NOW()),
  (3, 'تعمیرات تخصصی', 'banners/repair_service.jpg', TRUE, 3, NOW(), NOW()),
  (4, 'بازی‌های جدید', 'banners/new_games.jpg', FALSE, 4, NOW(), NOW());

SELECT setval('website_homebanner_id_seq', (SELECT MAX(id) FROM website_homebanner));
```

---

## Quick Reference: Execution Order

| # | Table | Depends on |
|---|-------|-----------|
| 1 | `users_customuser` | — |
| 2 | `users_mainmanager` | `users_customuser` |
| 3 | `users_otp` | `users_customuser` |
| 4 | `users_apikey` | — |
| 5 | `hr_employeerole` | — |
| 6 | `hr_employee` | `users_customuser`, `hr_employeerole` |
| 7 | `hr_repairman` | `users_customuser` |
| 8 | `hr_employeefile` | `hr_employee` |
| 9 | `hr_employeerequest` | `hr_employee` |
| 10 | `hr_employeehire` | `users_customuser` |
| 11 | `crm_customer` | `users_customuser` |
| 12 | `inventory_supplier` | — |
| 13 | `inventory_productcategory` | — |
| 14 | `inventory_productcolor` | — |
| 15 | `inventory_productcompany` | — |
| 16 | `inventory_product` | `productcolor`, `productcategory`, `productcompany` |
| 17 | `inventory_productimage` | `product` |
| 18 | `inventory_sonyaccountstatus` | — |
| 19 | `inventory_sonyaccountbank` | — |
| 20 | `inventory_game` | — |
| 21 | `inventory_gameimage` | `game` |
| 22 | `inventory_sonyaccount` | `hr_employee`, `sonyaccountstatus`, `sonyaccountbank` |
| 23 | `inventory_sonyaccountgame` | `sonyaccount`, `game` |
| 24–29 | `inventory_doc*`, `realassets*` | various |
| 30 | `accounting_bankaccount` | — |
| 31 | `accounting_accountside` | `django_content_type` |
| 32 | `accounting_invoicecategory` | — |
| 33 | `accounting_invoice` | `accountside`, `invoicecategory` |
| 34 | `accounting_invoiceitem` | `invoice`, `django_content_type` |
| 35 | `accounting_payrolldetail` | `invoice` |
| 36 | `accounting_transaction` | `invoice`, `accountside`, `bankaccount` |
| 37 | `task_manager_plannedtask` | `hr_employee` |
| 38–39 | `task_manager_dailytask*` | `hr_employee` |
| 40 | `messenger_chatroom` | `users_customuser` |
| 41 | `messenger_membership` | `users_customuser`, `chatroom` |
| 42 | `messenger_message` | `chatroom`, `users_customuser` |
| 43–54 | `orders_*` | `crm_customer`, `hr_employeerole`, `accounting_invoice`, `inventory_sonyaccount`, `hr_employee` |
| 55–65 | `website_*` | `crm_customer`, `inventory_product`, `inventory_game`, `users_customuser` |

> ⚠️ **Before running:** Replace password hashes in `users_customuser` with real Django hashes.
> You can generate them with: `python manage.py shell -c "from django.contrib.auth.hashers import make_password; print(make_password('YourPassword'))"`
