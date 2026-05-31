(function() {
    // Функция добавления декоративных полос с узорами
    function addImageBorders() {
        // Путь к вашему изображению (поместите файл в static/images/)
        const leftImageUrl = '/static/images/patternss.jpg';
        const rightImageUrl = '/static/images/patternss.jpg';
        const borderWidth = '500px';
        const leftMargin = 300;
        const rightMargin = 40;

        // Удаляем старые полосы, если перезагружаем скрипт
        const oldLeft = document.querySelector('.border-left-img');
        const oldRight = document.querySelector('.border-right-img');
        if (oldLeft) oldLeft.remove();
        if (oldRight) oldRight.remove();

        // Создаём левую полосу
        const leftBorder = document.createElement('div');
        leftBorder.className = 'image-border-left';
        leftBorder.style.cssText = `
            position: fixed;
            top: 0;
            left: ${leftMargin}px;
            width: ${borderWidth};
            height: 100%;
            background-image: url('${leftImageUrl}');
            background-repeat: repeat-y;
            background-position: left top;
            background-size: auto 100%;
            pointer-events: none;
            z-index: 999;
            opacity: 0.7;
        `;
        document.body.prepend(leftBorder);

        // Создаём правую полосу
        const rightBorder = document.createElement('div');
        rightBorder.className = 'image-border-right';
        rightBorder.style.cssText = `
            position: fixed;
            top: 0;
            
            right: ${rightMargin}px;
            width: ${borderWidth};
            height: 100%;
            background-image: url('${rightImageUrl}');
            background-repeat: repeat-y;
            background-position: right top;
            background-size: auto 100%;
            pointer-events: none;
            z-index: 999;
            opacity: 0.7;
        `;
        document.body.prepend(rightBorder);

        // Добавляем стили для адаптивности (если ещё не добавлены)
        if (!document.getElementById('border-styles')) {
            const style = document.createElement('style');
            style.id = 'border-styles';
            style.textContent = `
                @media (max-width: 768px) {
                    .border-left-img, .border-right-img {
                        width: 60px !important;
                        opacity: 0.4 !important;
                    }
                }
                @media (max-width: 480px) {
                    .border-left-img, .border-right-img {
                        display: none;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        console.log('Полосы с узорами добавлены. Ширина:', borderWidth);
    }

    // Запускаем после полной загрузки DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addImageBorders);
    } else {
        addImageBorders();
    }
})();