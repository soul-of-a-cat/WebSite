// Main JavaScript for forum functionality

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

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

// Profile avatar functionality
function initProfileAvatar() {
    const fileInput = document.getElementById('id_profile-image');
    const removeBtn = document.getElementById('remove-avatar');
    const clearAvatarInput = document.getElementById('avatar-clear');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const avatarPreviewContainer = document.querySelector('.avatar-preview');

    console.log('Initializing profile avatar:', {
        fileInput: !!fileInput,
        removeBtn: !!removeBtn,
        clearAvatarInput: !!clearAvatarInput,
        avatarPreviewContainer: !!avatarPreviewContainer
    });

    // Обработка выбора файла
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            console.log('File input changed:', this.files);
            if (this.files && this.files[0]) {
                const file = this.files[0];

                // Проверка типа файла
                if (!file.type.startsWith('image/')) {
                    alert('Пожалуйста, выберите файл изображения');
                    this.value = '';
                    return;
                }

                // Проверка размера файла (макс 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    alert('Файл слишком большой. Максимальный размер: 5MB');
                    this.value = '';
                    return;
                }

                fileName.textContent = file.name;
                fileInfo.style.display = 'block';

                // Сбрасываем флаг удаления, если пользователь выбрал новое фото
                clearAvatarInput.value = 'false';

                // Показываем кнопку удаления
                if (removeBtn) {
                    removeBtn.style.display = 'block';
                }

                // Предпросмотр выбранного изображения
                const reader = new FileReader();
                reader.onload = function(e) {
                    const currentPreview = document.getElementById('avatar-preview');
                    if (currentPreview && currentPreview.tagName === 'IMG') {
                        currentPreview.src = e.target.result;
                    } else {
                        // Если это placeholder, заменяем его на img
                        const newImg = document.createElement('img');
                        newImg.src = e.target.result;
                        newImg.alt = 'Аватар';
                        newImg.className = 'avatar-image';
                        newImg.id = 'avatar-preview';
                        avatarPreviewContainer.innerHTML = '';
                        avatarPreviewContainer.appendChild(newImg);
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Обработка удаления фото
    if (removeBtn) {
        removeBtn.addEventListener('click', function() {
            if (confirm('Вы уверены, что хотите удалить фото?')) {
                // Устанавливаем флаг удаления
                clearAvatarInput.value = 'true';

                // Сбрасываем file input
                if (fileInput) {
                    fileInput.value = '';
                }

                // Скрываем информацию о файле
                if (fileInfo) {
                    fileInfo.style.display = 'none';
                }

                // Восстанавливаем placeholder
                const currentPreview = document.getElementById('avatar-preview');
                if (currentPreview && avatarPreviewContainer) {
                    const placeholder = document.createElement('div');
                    placeholder.className = 'avatar-placeholder';
                    placeholder.id = 'avatar-preview';
                    placeholder.innerHTML = '<i class="fas fa-user-circle"></i>';
                    avatarPreviewContainer.innerHTML = '';
                    avatarPreviewContainer.appendChild(placeholder);
                }

                // Скрываем кнопку удаления
                this.style.display = 'none';
            }
        });
    }
}

// Form validation for profile
function initProfileForm() {
    const profileForm = document.querySelector('.profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            const emailField = document.getElementById('id_user-email');
            if (emailField && !emailField.value.trim()) {
                e.preventDefault();
                alert('Поле email обязательно для заполнения');
                emailField.focus();
                return;
            }

            // Validate birth date if provided
            const birthDateField = document.getElementById('id_profile-birthday');
            if (birthDateField && birthDateField.value) {
                const birthDate = new Date(birthDateField.value);
                const today = new Date();
                if (birthDate > today) {
                    e.preventDefault();
                    alert('Дата рождения не может быть в будущем');
                    birthDateField.focus();
                    return;
                }
            }
        });
    }
}

// Posts functionality
function initPosts() {
    // Dropdown menus
    const dropdowns = document.querySelectorAll('.dropdown');

    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function() {
        dropdowns.forEach(dropdown => {
            const menu = dropdown.querySelector('.dropdown-menu');
            if (menu) {
                menu.style.opacity = '0';
                menu.style.visibility = 'hidden';
                menu.style.transform = 'translateY(-10px)';
            }
        });
    });

    // Confirm delete actions for dropdown items
    const deleteLinks = document.querySelectorAll('.dropdown-item.delete');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить этот пост?')) {
                e.preventDefault();
            }
        });
    });

    // Lazy loading for images
    const images = document.querySelectorAll('.image-item img');
    images.forEach(img => {
        if (img.complete) {
            img.style.opacity = '1';
        } else {
            img.addEventListener('load', function() {
                this.style.opacity = '1';
            });
            img.addEventListener('error', function() {
                this.style.opacity = '1';
            });
        }
    });
}

// File selection handler
function handleFileSelect(e) {
    const files = e.target.files;
    const maxFiles = 10;

    // Проверка количества файлов
    if (files.length > maxFiles) {
        alert(`Максимальное количество изображений: ${maxFiles}`);
        this.value = '';
        return;
    }

    // Проверка каждого файла
    for (let file of files) {
        // Проверка размера файла (макс 5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert(`Файл "${file.name}" слишком большой. Максимальный размер: 5MB`);
            this.value = '';
            return;
        }

        // Проверка типа файла
        if (!file.type.startsWith('image/')) {
            alert(`Файл "${file.name}" не является изображением`);
            this.value = '';
            return;
        }
    }

    // Создаем превью изображений
    createImagePreviews(this, files);
}

// Create image previews
function createImagePreviews(input, files) {
    // Удаляем существующие превью
    const existingPreviews = input.parentNode.querySelector('.image-previews');
    if (existingPreviews) {
        existingPreviews.remove();
    }

    if (files.length === 0) return;

    // Создаем контейнер для превью
    const previewsContainer = document.createElement('div');
    previewsContainer.className = 'image-previews';

    // Создаем превью для каждого файла
    Array.from(files).forEach(file => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.createElement('div');
            preview.className = 'image-preview-item';

            const img = document.createElement('img');
            img.src = e.target.result;
            img.style.maxWidth = '100px';
            img.style.maxHeight = '100px';

            const fileName = document.createElement('div');
            fileName.textContent = file.name;
            fileName.style.fontSize = '12px';
            fileName.style.marginTop = '5px';

            preview.appendChild(img);
            preview.appendChild(fileName);
            previewsContainer.appendChild(preview);
        };
        reader.readAsDataURL(file);
    });

    input.parentNode.appendChild(previewsContainer);
}

// Initialize file inputs
function initFileInputs() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        if (!input.id.includes('profile-image')) { // Не применяем к аватару
            input.addEventListener('change', handleFileSelect);
        }
    });
}

// Post create functionality
function initPostCreate() {
    const addImageBtn = document.getElementById('add-image');
    const imageForms = document.getElementById('image-forms');
    const totalForms = document.getElementById('id_images-TOTAL_FORMS');

    if (addImageBtn && totalForms && imageForms) {
        let formCount = parseInt(totalForms.value);

        addImageBtn.addEventListener('click', function() {
            const maxForms = 10;
            if (formCount >= maxForms) {
                alert('Максимальное количество изображений: ' + maxForms);
                return;
            }

            const newForm = document.createElement('div');
            newForm.className = 'image-form-item';
            newForm.innerHTML = `
                <div class="form-group">
                    <label>Изображение ${formCount + 1}</label>
                    <input type="file" name="images-${formCount}-image" class="form-control" id="id_images-${formCount}-image">
                    <input type="hidden" name="images-${formCount}-id" id="id_images-${formCount}-id">
                    <input type="hidden" name="images-${formCount}-post" id="id_images-${formCount}-post">
                </div>
            `;
            imageForms.appendChild(newForm);
            totalForms.value = formCount + 1;
            formCount++;

            // Добавляем обработчик для нового поля
            const newFileInput = newForm.querySelector('input[type="file"]');
            newFileInput.addEventListener('change', handleFileSelect);
        });
    }

    initFileInputs();
}

// Post update functionality
function initPostUpdate() {
    const addImageBtn = document.getElementById('add-image');
    const imageForms = document.getElementById('image-forms');
    const totalForms = document.getElementById('id_images-TOTAL_FORMS');

    if (addImageBtn && totalForms && imageForms) {
        let formCount = parseInt(totalForms.value);

        addImageBtn.addEventListener('click', function() {
            const maxForms = 10;
            if (formCount >= maxForms) {
                alert('Максимальное количество изображений: ' + maxForms);
                return;
            }

            const newForm = document.createElement('div');
            newForm.className = 'image-form-item';
            newForm.innerHTML = `
                <div class="form-group">
                    <label>Новое изображение</label>
                    <input type="file" name="images-${formCount}-image" class="form-control" id="id_images-${formCount}-image">
                    <input type="hidden" name="images-${formCount}-id" id="id_images-${formCount}-id">
                    <input type="hidden" name="images-${formCount}-post" id="id_images-${formCount}-post">
                    <input type="hidden" name="images-${formCount}-DELETE" id="id_images-${formCount}-DELETE">
                </div>
            `;
            imageForms.appendChild(newForm);
            totalForms.value = formCount + 1;
            formCount++;

            // Добавляем обработчик для нового поля
            const newFileInput = newForm.querySelector('input[type="file"]');
            newFileInput.addEventListener('change', handleFileSelect);
        });
    }

    initFileInputs();
}

// Post delete confirmation
function initPostDelete() {
    const deleteForm = document.querySelector('.delete-form');

    if (deleteForm) {
        deleteForm.addEventListener('submit', function(e) {
            if (!confirm('Вы уверены, что хотите удалить этот пост? Это действие нельзя отменить.')) {
                e.preventDefault();
            }
        });
    }
}

// Initialize post forms based on current page
function initPostForms() {
    const updateContainer = document.querySelector('.post-update-container');
    const deleteContainer = document.querySelector('.post-delete-container');
    const createContainer = document.querySelector('.post-create-container');

    if (updateContainer) {
        initPostUpdate();
    }

    if (deleteContainer) {
        initPostDelete();
    }

    if (createContainer) {
        initPostCreate();
    }
}

// Main initialization function
function initForum() {
    console.log('Initializing forum functionality...');

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });

        // Initial resize
        setTimeout(() => {
            textarea.style.height = 'auto';
            textarea.style.height = (textarea.scrollHeight) + 'px';
        }, 100);
    });

    // Confirm delete actions for links
    const deleteLinks = document.querySelectorAll('a[href*="delete"]');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить этот элемент?')) {
                e.preventDefault();
            }
        });
    });

    // Smooth scroll to anchors
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Markdown helper for textareas
    const markdownTextareas = document.querySelectorAll('textarea[name="content"]');
    markdownTextareas.forEach(textarea => {
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = this.selectionStart;
                const end = this.selectionEnd;

                this.value = this.value.substring(0, start) + '    ' + this.value.substring(end);
                this.selectionStart = this.selectionEnd = start + 4;
            }
        });
    });

    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                if (message.parentNode) {
                    message.remove();
                }
            }, 300);
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let valid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.style.borderColor = '#dc3545';
                    field.classList.add('error-field');
                } else {
                    field.style.borderColor = '';
                    field.classList.remove('error-field');
                }
            });

            if (!valid) {
                e.preventDefault();
                alert('Пожалуйста, заполните все обязательные поля.');
            }
        });
    });

    // Initialize specific functionality based on page
    initProfileAvatar();
    initProfileForm();
    initPosts();
    initPostForms();
    initCommentForms();
    initCommentFormValidation();
    initAuthForms();
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', initForum);

// Export functions for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatDate,
        debounce,
        initForum
    };
}

// Form initialization for auth forms
function initAuthForms() {
    const authForms = document.querySelectorAll('.auth-form form');

    authForms.forEach(form => {
        // Добавляем валидацию при отправке
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            const inputs = this.querySelectorAll('input[required]');
            let isValid = true;

            // Проверяем обязательные поля
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    markFieldAsInvalid(input);
                } else {
                    markFieldAsValid(input);
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Пожалуйста, заполните все обязательные поля');
                return;
            }

            // Если форма валидна, показываем состояние загрузки
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Вход...';

                // Автоматически восстанавливаем кнопку через 5 секунд на случай ошибки
                setTimeout(() => {
                    if (submitBtn.disabled) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = 'Войти';
                    }
                }, 5000);
            }
        });

        // Добавляем live validation
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.hasAttribute('required') && !this.value.trim()) {
                    markFieldAsInvalid(this);
                } else {
                    markFieldAsValid(this);
                }
            });

            input.addEventListener('input', function() {
                if (this.classList.contains('invalid')) {
                    if (this.value.trim()) {
                        markFieldAsValid(this);
                    }
                }
            });
        });
    });
}

function validateField(field) {
    if (field.checkValidity()) {
        field.classList.remove('error-field');
        field.style.borderColor = '#28a745';
    } else {
        field.classList.add('error-field');
        field.style.borderColor = '#dc3545';
    }
}

function markFieldAsInvalid(field) {
    field.classList.add('invalid');
    field.classList.remove('valid');
    field.style.borderColor = '#dc3545';

    // Показываем ошибку, если её ещё нет
    let errorElement = field.parentNode.querySelector('.field-error');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'field-error error';
        errorElement.textContent = 'Это поле обязательно для заполнения';
        field.parentNode.appendChild(errorElement);
    }
}

function markFieldAsValid(field) {
    field.classList.add('valid');
    field.classList.remove('invalid');
    field.style.borderColor = '#28a745';

    // Убираем сообщение об ошибке
    const errorElement = field.parentNode.querySelector('.field-error');
    if (errorElement) {
        errorElement.remove();
    }
}

// Comment forms functionality
function initCommentForms() {
    console.log('Initializing comment forms...');

    const addBtn = document.getElementById('add-comment-image');
    const formsContainer = document.getElementById('comment-image-forms');
    const totalForms = document.getElementById('id_comment_images-TOTAL_FORMS');

    console.log('Comment form elements:', {
        addBtn: !!addBtn,
        formsContainer: !!formsContainer,
        totalForms: !!totalForms
    });

    if (addBtn && formsContainer && totalForms) {
        let formCount = parseInt(totalForms.value);
        console.log('Initial form count:', formCount);

        addBtn.addEventListener('click', function() {
            console.log('Add comment image button clicked, current count:', formCount);

            const maxForms = 5;
            if (formCount >= maxForms) {
                alert('Максимальное количество изображений для комментария: ' + maxForms);
                return;
            }

            // Создаем новую форму
            const newForm = document.createElement('div');
            newForm.className = 'image-form-item comment-image-form';
            newForm.innerHTML = `
                <div class="form-group">
                    <label>Изображение ${formCount + 1}</label>
                    <input type="file" name="comment_images-${formCount}-image"
                           class="form-control"
                           accept="image/*">
                </div>
            `;

            formsContainer.appendChild(newForm);
            formCount++;
            totalForms.value = formCount;

            console.log('New comment form added, total forms now:', formCount);
        });

        console.log('Comment form handler attached successfully');
    } else {
        console.log('Some comment form elements are missing');
    }
}

// Comment form validation
function initCommentFormValidation() {
    const commentForms = document.querySelectorAll('form[enctype="multipart/form-data"]');

    commentForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const textarea = this.querySelector('textarea[name="text"]');
            const fileInputs = this.querySelectorAll('input[type="file"]');
            let hasFiles = false;

            // Проверяем, есть ли выбранные файлы
            fileInputs.forEach(input => {
                if (input.files && input.files.length > 0) {
                    hasFiles = true;
                }
            });

            // Проверяем текст комментария
            if (textarea && !textarea.value.trim()) {
                e.preventDefault();
                alert('Пожалуйста, введите текст комментария');
                textarea.focus();
                return;
            }

            // Проверяем количество файлов
            if (hasFiles) {
                let totalFiles = 0;
                fileInputs.forEach(input => {
                    if (input.files) {
                        totalFiles += input.files.length;
                    }
                });

                if (totalFiles > 5) {
                    e.preventDefault();
                    alert('Максимальное количество изображений для комментария: 5');
                    return;
                }
            }
        });
    });
}