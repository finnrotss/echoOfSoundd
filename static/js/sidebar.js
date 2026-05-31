document.addEventListener('DOMContentLoaded', function() {
      const sidebar = document.querySelector('.sidebar');
    const body = document.body;

    let burgerBtn = document.querySelector('.sidebar-burger');
    if (!burgerBtn) {
        burgerBtn = document.createElement('button');
        burgerBtn.className = 'sidebar-burger';
        burgerBtn.innerHTML = '☰';
        burgerBtn.setAttribute('aria-label', 'Открыть меню');
        body.insertBefore(burgerBtn, body.firstChild);
    }

    let overlay = document.querySelector('.sidebar-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        body.appendChild(overlay);
    }

    function openSidebar() {
        if (!sidebar) return;
        sidebar.classList.add('sidebar-open');
        overlay.classList.add('active');
        body.style.overflow = 'hidden';
        if (localStorage) localStorage.setItem('sidebarState', 'open');
    }
    function closeSidebar() {
        if (!sidebar) return;
        sidebar.classList.remove('sidebar-open');
        overlay.classList.remove('active');
        body.style.overflow = '';
        if (localStorage) localStorage.setItem('sidebarState', 'closed');
    }
    function toggleSidebar() {
        if (sidebar.classList.contains('sidebar-open')) closeSidebar();
        else openSidebar();
    }

    if (burgerBtn) burgerBtn.addEventListener('click', (e) => { e.stopPropagation(); toggleSidebar(); });
    if (overlay) overlay.addEventListener('click', closeSidebar);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar && sidebar.classList.contains('sidebar-open')) closeSidebar();
    });
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768 && sidebar && sidebar.classList.contains('sidebar-open')) closeSidebar();
    });
    if (localStorage && localStorage.getItem('sidebarState') === 'open' && window.innerWidth <= 768) openSidebar();

    //
    document.querySelectorAll('.sidebar-nav a').forEach(link => {
        const text = link.innerText.trim();
        if (menuIcons[text] && !link.querySelector('.menu-icon')) {
            const iconSpan = document.createElement('span');
            iconSpan.className = 'menu-icon';
            iconSpan.textContent = menuIcons[text];
            iconSpan.style.marginRight = '12px';
            iconSpan.style.fontSize = '1.2rem';
            link.prepend(iconSpan);
        }
    });

    const userAvatar = document.querySelector('.user-avatar');
    if (userAvatar && !userAvatar.querySelector('.user-icon')) {
        userAvatar.style.display = 'flex';
        userAvatar.style.alignItems = 'center';
        userAvatar.style.justifyContent = 'center';
        // если внутри уже есть текст (первая буква), оставляем, иначе ставим иконку
        if (!userAvatar.innerText.trim()) userAvatar.innerText = '👤';
    }

    // Ссылка "Мой профиль" – добавить иконку
    const profileLink = document.querySelector('.sidebar-user a[href*="my_profile"]');
    if (profileLink && !profileLink.querySelector('.menu-icon')) {
        const icon = document.createElement('span');
        icon.className = 'menu-icon';
        icon.textContent = '👤';
        icon.style.marginRight = '8px';
        profileLink.prepend(icon);
    }

    // Ссылка "Выход"
    const logoutLink = document.querySelector('.sidebar-user a[href*="logout"]');
    if (logoutLink && !logoutLink.querySelector('.menu-icon')) {
        const icon = document.createElement('span');
        icon.className = 'menu-icon';
        icon.style.marginRight = '8px';
        logoutLink.prepend(icon);
    }

    // Для неавторизованных кнопок "Вход" и "Регистрация" (они имеют классы btn)
    const loginBtn = document.querySelector('.sidebar-user .btn-primary');
    if (loginBtn && loginBtn.innerText.includes('Вход') && !loginBtn.querySelector('.menu-icon')) {
        const icon = document.createElement('span');
        icon.style.marginRight = '8px';
        loginBtn.prepend(icon);
    }
    const regBtn = document.querySelector('.sidebar-user .btn-outline');
    if (regBtn && regBtn.innerText.includes('Регистрация') && !regBtn.querySelector('.menu-icon')) {
        const icon = document.createElement('span');
        icon.textContent = '✍️';
        icon.style.marginRight = '8px';
        regBtn.prepend(icon);
    }

    // Добавляем дополнительный класс для более плотного стиля (как на втором фото)
    const sidebarNav = document.querySelector('.sidebar-nav');
    if (sidebarNav) sidebarNav.classList.add('modern-menu');

    // Делаем активный пункт меню более заметным (уже есть в CSS, но можно усилить)
    const activeLink = document.querySelector('.sidebar-nav a.active');
    if (activeLink) {
        activeLink.style.borderLeft = `3px solid var(--primary-color)`;
        activeLink.style.backgroundColor = `var(--bg-hover)`;
    }

    // --------------------------------------------------------------
    // 3. ПОДСКАЗКИ ДЛЯ ДЛИННЫХ ТРЕКОВ (оставляем)
    // --------------------------------------------------------------
    document.querySelectorAll('.track-title').forEach(title => {
        if (title.scrollWidth > title.clientWidth) title.setAttribute('title', title.textContent);
    });

    // --------------------------------------------------------------
    // 4. ГОРИЗОНТАЛЬНЫЙ СКРОЛЛ ЖАНРОВ (drag-to-scroll)
    // --------------------------------------------------------------
    const scrollContainer = document.querySelector('.genres-scroll');
    if (scrollContainer) {
        let isDown = false, startX, scrollLeft;
        scrollContainer.addEventListener('mousedown', (e) => {
            isDown = true;
            startX = e.pageX - scrollContainer.offsetLeft;
            scrollLeft = scrollContainer.scrollLeft;
        });
        scrollContainer.addEventListener('mouseleave', () => isDown = false);
        scrollContainer.addEventListener('mouseup', () => isDown = false);
        scrollContainer.addEventListener('mousemove', (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - scrollContainer.offsetLeft;
            const walk = (x - startX) * 2;
            scrollContainer.scrollLeft = scrollLeft - walk;
        });
    }

    console.log('sidebar.js:');
});