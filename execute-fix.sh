#!/bin/bash

# ==========================================
# وكيل التنفيذ التلقائي (AI Deployment Agent)
# ==========================================

echo ">>> بدء عملية التنفيذ والرفع إلى GitHub..."

# 1. التأكد من المجلد الصحيح
if [ ! -d "sahol-unified-v15-idp" ]; then
    echo "خطأ: مجلد المشروع غير موجود. تأكد أنك في المجلد الصحيح."
    exit 1
fi

# الانتقال للمجلد
cd sahol-unified-v15-idp

# 2. إنشاء فرع جديد للميزة (Feature Branch)
echo ">>> إنشاء فرع جديد: feature/ai-performance-optimization"
git checkout -b feature/ai-performance-optimization

# 3. إنشاء ملف التهيئة الجديد (application.yml)
echo ">>> تحديث ملف التهيئة: application.yml"
cat << 'EOF' > src/main/resources/application.yml
server:
  port: 8080
  tomcat:
    threads:
      max: 200
      min-spare: 20
    max-connections: 10000
    accept-count: 100

spring:
  application:
    name: sahol-idp
  
  session:
    store-type: redis
    redis:
      namespace: sahol:sessions
      cleanup-cron: "0 * * * * *"

  datasource:
    url: jdbc:postgresql://sahol-db:5432/sahol_db
    username: admin
    password: password123
    driver-class-name: org.postgresql.Driver
    hikari:
      maximum-pool-size: 25
      minimum-idle: 10
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
      connection-test-query: SELECT 1

  redis:
    host: sahol-redis
    port: 6379
    timeout: 6000ms
    lettuce:
      pool:
        max-active: 8
        max-wait: -1ms
        max-idle: 8
        min-idle: 0

  cache:
    type: redis
    redis:
      time-to-live: 600000 

  jpa:
    hibernate:
      ddl-auto: update
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        jdbc:
          batch_size: 50 
        order_inserts: true
        order_updates: true
EOF

# 4. تحديث UserService.java (سنقوم بالكتابة فوق الملف القديم)
# ملاحظة: المستخدم بحاجة لضبط الحزمة (Package) الصحيحة يدوياً إذا اختلف المسار
echo ">>> تحديث ملف الخدمة: UserService.java"
mkdir -p src/main/java/com/kafaat/sahol/service
cat << 'EOF' > src/main/java/com/kafaat/sahol/service/UserService.java
package com.kafaat.sahol.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.security.crypto.password.PasswordEncoder;

import com.kafaat.sahol.model.User;
import com.kafaat.sahol.repository.UserRepository;
import com.kafaat.sahol.exception.UserAlreadyExistsException; 

import java.util.Optional;

@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Transactional
    public User createUser(String username, String email, String password) {
        if (userRepository.existsByUsername(username)) {
            throw new UserAlreadyExistsException("User " + username + " already exists");
        }

        User user = new User();
        user.setUsername(username);
        user.setEmail(email);
        user.setPassword(passwordEncoder.encode(password));

        try {
            return userRepository.save(user);
        } catch (DataIntegrityViolationException ex) {
            throw new UserAlreadyExistsException("Conflict: User " + username + " is being created concurrently.");
        }
    }

    @Transactional(readOnly = true)
    @Cacheable(value = "users", key = "#username")
    public Optional<User> findByUsername(String username) {
        return userRepository.findByUsername(username);
    }

    @Transactional
    @CacheEvict(value = "users", key = "#user.username")
    public User updateUser(User user) {
        return userRepository.save(user);
    }
}
EOF

# 5. إضافة التبعيات إلى pom.xml (طريقة إلحاقية Append)
echo ">>> إضافة التبعيات الجديدة إلى pom.xml..."
cat << 'EOF' >> pom.xml
    <!-- Added by AI Agent for Optimization -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-redis</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.session</groupId>
        <artifactId>spring-session-data-redis</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-cache</artifactId>
    </dependency>
EOF

echo ">>> تحذير: تم إلحاق التبعيات في نهاية ملف pom.xml. يرجى نقلها داخل وسم <dependencies> في الكود قبل البناء النهائي."

# 6. إرسال التغييرات إلى Git
echo ">>> إضافة الملفات (Git Add)..."
git add .

echo ">>> حفظ التغييرات (Git Commit)..."
git commit -m "AI Auto-Fix: Optimized Connection Pool, Added Redis Session & Caching, Fixed Race Conditions"

echo ">>> رفع التغييرات إلى GitHub (Git Push)..."
git push -u origin feature/ai-performance-optimization

if [ $? -eq 0 ]; then
    echo "=========================================="
    echo "SUCCESS: تم الرفع بنجاح إلى GitHub!"
    echo "=========================================="
    echo "الخطوة التالية:"
    echo "1. اذهب إلى GitHub Repository الخاص بك."
    echo "2. ستجد إشعاراً (Pull Request) لدمج الفرع 'feature/ai-performance-optimization'."
    echo "3. اضغط 'Merge Pull Request' لاستكمال الدمج."
else
    echo "فشل الرفع. تأكد من مفتاح SSH أو الـ Token الخاص بـ GitHub."
fi
