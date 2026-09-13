document.addEventListener('DOMContentLoaded', () => {
    
    // 1. SMOOTH SCROLLING FOR NAVIGATION LINKS
    // Select all anchor links that start with '#'
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault(); // Prevent default jump
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                // Scroll smoothly to the section
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });


    /* =========================================
   DROPDOWN TOGGLE FOR MOBILE
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    if (dropdownToggle) {
        dropdownToggle.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent click from bubbling up
            dropdownMenu.classList.toggle('show');
        });

        // Close dropdown if clicked outside
        document.addEventListener('click', () => {
            dropdownMenu.classList.remove('show');
        });
    }
});

    // 2. AUTO IMAGE SLIDER LOGIC
    const slides = document.querySelectorAll('.slider-image');
    let currentSlide = 0;
    const slideInterval = 5000; // 5000 milliseconds = 5 seconds

    if (slides.length > 0) {
        function nextSlide() {
            slides[currentSlide].classList.remove('active');
            currentSlide = (currentSlide + 1) % slides.length;
            slides[currentSlide].classList.add('active');
        }
        setInterval(nextSlide, slideInterval);
    }

    // 3. DYNAMIC LANGUAGE TRANSLATION LOGIC
    const langButtons = document.querySelectorAll('.lang-btn');
    
    // Function to translate the page
    function translatePage(lang) {
        // Find all elements that have a translation attribute for the chosen language
        const elementsToTranslate = document.querySelectorAll(`[data-${lang}]`);
        
        elementsToTranslate.forEach(element => {
            const translatedText = element.getAttribute(`data-${lang}`);
            if (translatedText) {
                // Use innerHTML to preserve HTML entities like &copy; if present
                element.innerHTML = translatedText;
            }
        });
    }

    // Add click events to language buttons
    langButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Update active button styling
            langButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            // Get the selected language (en, hi, or mr)
            const selectedLang = button.getAttribute('data-lang');
            
            // Translate the page
            translatePage(selectedLang);
            
            console.log(`Language switched to: ${selectedLang}`);
        });
    });
});