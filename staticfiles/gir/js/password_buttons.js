document.addEventListener('DOMContentLoaded', function() {
    // Находим поле пароля
    const passwordField = document.querySelector('input[name="password"]');
    if (passwordField) {
        // Создаем контейнер для кнопок
        const buttonContainer = document.createElement('div');
        buttonContainer.style.marginTop = '10px';
        
        // Кнопка генерации
        const generateBtn = document.createElement('button');
        generateBtn.type = 'button';
        generateBtn.className = 'btn btn-success btn-sm';
        generateBtn.innerHTML = '🔄 Згенерувати новий пароль';
        generateBtn.onclick = function() {
            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
            let password = '';
            for (let i = 0; i < 12; i++) {
                password += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            passwordField.value = password;
            passwordField.type = 'text';
            
            // Показываем кнопку копирования
            copyBtn.style.display = 'inline-block';
            
            alert('Новий пароль згенеровано: ' + password + '\n\nНе забудьте зберегти зміни!');
        };
        
        // Кнопка копирования (изначально скрыта)
        const copyBtn = document.createElement('button');
        copyBtn.type = 'button';
        copyBtn.className = 'btn btn-info btn-sm';
        copyBtn.style.display = 'none';
        copyBtn.style.marginLeft = '10px';
        copyBtn.innerHTML = '📋 Скопіювати дані для доступу';
        copyBtn.onclick = function() {
            const username = document.querySelector('input[name="username"]').value;
            const password = passwordField.value;
            
            if (!username || !password) {
                alert('Спочатку заповніть логін та згенеруйте пароль!');
                return;
            }
            
            const accessData = `Доступ на gir.generacia.energy:\nЛогін: ${username}\nПароль: ${password}`;
            
            navigator.clipboard.writeText(accessData).then(function() {
                alert('Дані для доступу скопійовано в буфер!');
            }).catch(function(err) {
                // Fallback для старых браузеров
                const textArea = document.createElement('textarea');
                textArea.value = accessData;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('Дані для доступу скопійовано в буфер!');
            });
        };
        
        // Добавляем кнопки
        buttonContainer.appendChild(generateBtn);
        buttonContainer.appendChild(copyBtn);
        
        // Вставляем после поля пароля
        passwordField.parentNode.appendChild(buttonContainer);
    }
});
