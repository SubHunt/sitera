// Основные функции для сайта Sitera

document.addEventListener("DOMContentLoaded", function () {
    // Инициализация мобильного меню
    initMobileMenu();

    // Инициализация поиска
    initSearch();

    // Инициализация маски телефона
    initPhoneMask();

    // Инициализация формы обратной связи
    initContactForm();

    // Инициализация анимаций при скролле
    initScrollAnimations();

    // Инициализация ленивой загрузки изображений
    initLazyLoading();

    // Инициализация карусели партнеров
    initPartnersCarousel();

    // Инициализация параллакса
    initParallax();

    // Инициализация функций каталога
    initCatalogFunctions();
});

// Маска для телефона
function initPhoneMask() {
    const phoneInputs = document.querySelectorAll(
        'input[type="tel"], input[name="phone"]'
    );

    phoneInputs.forEach((input) => {
        input.addEventListener("input", function (e) {
            let value = e.target.value.replace(/\D/g, "");
            let formattedValue = "";

            if (value.length > 0) {
                formattedValue = "+7";
            }

            if (value.length > 1) {
                formattedValue += " (" + value.substring(1, 4);
            }

            if (value.length > 4) {
                formattedValue += ") " + value.substring(4, 7);
            }

            if (value.length > 7) {
                formattedValue += "-" + value.substring(7, 9);
            }

            if (value.length > 9) {
                formattedValue += "-" + value.substring(9, 11);
            }

            e.target.value = formattedValue;
        });

        input.addEventListener("focus", function (e) {
            if (e.target.value === "") {
                e.target.value = "+7";
            }
        });

        input.addEventListener("blur", function (e) {
            if (e.target.value === "+7") {
                e.target.value = "";
            }
        });
    });
}

// Мобильное меню
function initMobileMenu() {
    const mobileMenuButton = document.getElementById("mobile-menu-button");
    const mobileMenu = document.getElementById("mobile-menu");

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener("click", function () {
            mobileMenu.classList.toggle("hidden");
            // Закрываем поиск при открытии меню
            const mobileSearch = document.getElementById("mobile-search");
            if (mobileSearch && !mobileSearch.classList.contains("hidden")) {
                mobileSearch.classList.add("hidden");
            }
        });
    }

    // Мобильный поиск
    const mobileSearchButton = document.getElementById("mobile-search-button");
    const mobileSearch = document.getElementById("mobile-search");

    if (mobileSearchButton && mobileSearch) {
        mobileSearchButton.addEventListener("click", function () {
            mobileSearch.classList.toggle("hidden");
            // Закрываем меню при открытии поиска
            if (mobileMenu && !mobileMenu.classList.contains("hidden")) {
                mobileMenu.classList.add("hidden");
            }
            // Фокус на поле поиска при открытии
            if (!mobileSearch.classList.contains("hidden")) {
                const searchInput = mobileSearch.querySelector("input");
                if (searchInput) {
                    searchInput.focus();
                }
            }
        });

        // Закрываем мобильные результаты поиска при клике на ссылку
        const mobileSearchResults = document.getElementById(
            "mobile-search-results"
        );
        if (mobileSearchResults) {
            mobileSearchResults.addEventListener("click", function (e) {
                if (e.target.tagName === "A") {
                    mobileSearch.classList.add("hidden");
                    mobileSearchResults.classList.add("hidden");
                }
            });
        }
    }

    // Закрывать меню и поиск при клике вне их
    document.addEventListener("click", function (e) {
        if (
            mobileMenuButton &&
            mobileMenu &&
            !mobileMenuButton.contains(e.target) &&
            !mobileMenu.contains(e.target) &&
            !e.target.closest("#mobile-search")
        ) {
            mobileMenu.classList.add("hidden");
        }

        if (
            mobileSearchButton &&
            mobileSearch &&
            !mobileSearchButton.contains(e.target) &&
            !mobileSearch.contains(e.target) &&
            !e.target.closest("#mobile-menu")
        ) {
            mobileSearch.classList.add("hidden");
        }
    });
}

// Поиск
function initSearch() {
    // Инициализация для поля поиска в хедере (десктоп)
    const headerSearchInput = document.getElementById("header-search-input");
    const headerSearchResults = document.getElementById(
        "header-search-results"
    );

    // Инициализация для мобильного поиска
    const mobileSearchInput = document.getElementById("mobile-search-input");
    const mobileSearchResults = document.getElementById(
        "mobile-search-results"
    );

    let searchTimeout;

    // Функция для настройки поиска
    function setupSearch(input, results) {
        if (!input) return;

        input.addEventListener("input", function () {
            clearTimeout(searchTimeout);
            const query = this.value.trim();

            if (query.length < 2) {
                if (results) {
                    results.classList.add("hidden");
                }
                return;
            }

            // Debounce поиск
            searchTimeout = setTimeout(() => {
                performSearch(query, results);
            }, 300);
        });

        // Закрытие поиска при клике вне
        if (results) {
            document.addEventListener("click", function (e) {
                if (
                    !input.contains(e.target) &&
                    !results.contains(e.target) &&
                    !e.target.closest("#mobile-search")
                ) {
                    results.classList.add("hidden");
                }
            });
        }
    }

    // Настраиваем десктопный поиск
    setupSearch(headerSearchInput, headerSearchResults);

    // Настраиваем мобильный поиск с выпадающими результатами
    setupSearch(mobileSearchInput, mobileSearchResults);
}

// Выполнение поиска
async function performSearch(query, resultsContainer) {
    if (!resultsContainer) return;

    const searchResults = resultsContainer;

    try {
        const response = await fetch(
            `/catalog/api/search/?q=${encodeURIComponent(query)}`
        );
        const data = await response.json();

        if (data.products && data.products.length > 0) {
            searchResults.innerHTML = data.products
                .map(
                    (product) => `
                <a href="${
                    product.url
                }" class="block p-4 hover:bg-gray-50 transition-colors border-b border-gray-200 last:border-b-0">
                    <div class="flex items-center space-x-3">
                        ${
                            product.image
                                ? `<img src="${product.image}" alt="${product.title}" class="w-12 h-12 object-cover rounded-lg shadow-sm">`
                                : `<div class="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                                    <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                    </svg>
                                  </div>`
                        }
                        <div class="flex-1 min-w-0">
                            <h4 class="font-medium text-gray-900 truncate">${
                                product.title
                            }</h4>
                            <p class="text-sm text-gray-600 truncate">${
                                product.category
                            }</p>
                            ${
                                product.article
                                    ? `<p class="text-xs text-gray-500">Артикул: ${product.article}</p>`
                                    : ""
                            }
                        </div>
                        <div class="flex-shrink-0">
                            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                            </svg>
                        </div>
                    </div>
                </a>
            `
                )
                .join("");
            searchResults.classList.remove("hidden");
        } else {
            searchResults.innerHTML = `
                <div class="p-6 text-center text-gray-500">
                    <svg class="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                    <p class="text-sm">Ничего не найдено по запросу "${query}"</p>
                    <p class="text-xs mt-1">Попробуйте изменить поисковый запрос</p>
                </div>
            `;
            searchResults.classList.remove("hidden");
        }
    } catch (error) {
        console.error("Search error:", error);
        searchResults.classList.add("hidden");
    }
}

// Форма обратной связи
function initContactForm() {
    // Обрабатываем форму на главной странице
    const contactForm = document.getElementById("contact-form");
    if (contactForm) {
        setupFormSubmission(contactForm, "/contacts/consultation/");
    }

    // Обрабатываем форму на странице контактов
    const contactPageForm = document.getElementById("contact-page-form");
    if (contactPageForm) {
        setupFormSubmission(contactPageForm, "/contacts/page/");
    }
}

// Функция для настройки отправки формы
function setupFormSubmission(form, url) {
    // Устанавливаем action для формы
    form.action = url;

    // Удаляем существующие обработчики событий
    form.removeEventListener("submit", handleFormSubmit);
    // Добавляем новый обработчик
    form.addEventListener("submit", handleFormSubmit);

    function handleFormSubmit(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;

        // Показываем индикатор загрузки
        submitBtn.disabled = true;
        submitBtn.textContent = "Отправка...";

        // Отправляем форму
        fetch(url, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
            },
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                return response.json();
            })
            .then((data) => {
                if (data.success) {
                    // Показываем сообщение об успехе
                    showMessage(data.message, "success");
                    form.reset();
                } else {
                    // Показываем ошибки
                    const errorMessages = Object.values(data.errors).flat();
                    showMessage(errorMessages.join("<br>"), "error");
                }
            })
            .catch((error) => {
                showMessage(
                    "Произошла ошибка при отправке формы. Пожалуйста, попробуйте еще раз.",
                    "error"
                );
            })
            .finally(() => {
                // Возвращаем кнопку в исходное состояние
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            });
    }
}

// Показ сообщений
function showMessage(message, type = "info") {
    const messageDiv = document.createElement("div");
    messageDiv.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-md ${
        type === "success"
            ? "bg-green-100 border border-green-400 text-green-700"
            : type === "error"
            ? "bg-red-100 border border-red-400 text-red-700"
            : "bg-blue-100 border border-blue-400 text-blue-700"
    }`;
    messageDiv.innerHTML = message;

    document.body.appendChild(messageDiv);

    // Анимация появления
    setTimeout(() => {
        messageDiv.style.opacity = "0";
        messageDiv.style.transform = "translateX(100%)";
        messageDiv.style.transition = "all 0.3s ease";

        setTimeout(() => {
            messageDiv.style.opacity = "1";
            messageDiv.style.transform = "translateX(0)";
        }, 10);
    }, 10);

    // Автоматическое удаление через 5 секунд
    setTimeout(() => {
        messageDiv.style.opacity = "0";
        messageDiv.style.transform = "translateX(100%)";

        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 300);
    }, 5000);
}

// Анимации при скролле
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px",
    };

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("animate-fadeInUp");
            }
        });
    }, observerOptions);

    // Наблюдаем за элементами с анимацией
    document
        .querySelectorAll(".feature-card, .category-card, .product-card")
        .forEach((el) => {
            observer.observe(el);
        });
}

// Ленивая загрузка изображений
function initLazyLoading() {
    const imageObserver = new IntersectionObserver(function (entries) {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove("lazy");
                imageObserver.unobserve(img);
            }
        });
    });

    document.querySelectorAll("img[data-src]").forEach((img) => {
        imageObserver.observe(img);
    });
}

// Плавная прокрутка к якорям
function smoothScrollTo(targetId) {
    const target = document.getElementById(targetId);
    if (target) {
        target.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });
    }
}

// Функция для анимации счетчиков
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);

    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = target + (element.dataset.suffix || "");
            clearInterval(timer);
        } else {
            element.textContent =
                Math.floor(start) + (element.dataset.suffix || "");
        }
    }, 16);
}

// Инициализация счетчиков статистики
function initCounters() {
    const counters = document.querySelectorAll("[data-counter]");

    const counterObserver = new IntersectionObserver(function (entries) {
        entries.forEach((entry) => {
            if (
                entry.isIntersecting &&
                !entry.target.classList.contains("animated")
            ) {
                const target = parseInt(entry.target.dataset.counter);
                animateCounter(entry.target, target);
                entry.target.classList.add("animated");
            }
        });
    });

    counters.forEach((counter) => {
        counterObserver.observe(counter);
    });
}

// Добавление CSS анимации
const style = document.createElement("style");
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-fadeInUp {
        animation: fadeInUp 0.6s ease-out;
    }
`;
document.head.appendChild(style);

// Инициализация счетчиков при загрузке страницы
initCounters();

// Добавляем интерактивные элементы для улучшения UX
function enhanceUserExperience() {
    // Плавная прокрутка к якорям
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener("click", function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute("href"));
            if (target) {
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                });
            }
        });
    });

    // Улучшенная мобильная навигация
    const mobileMenuButton = document.getElementById("mobile-menu-button");
    const mobileMenu = document.getElementById("mobile-menu");

    if (mobileMenuButton && mobileMenu) {
        // Закрывать меню при клике вне его
        document.addEventListener("click", function (e) {
            if (
                !mobileMenuButton.contains(e.target) &&
                !mobileMenu.contains(e.target)
            ) {
                mobileMenu.classList.add("hidden");
            }
        });

        // Закрывать меню при изменении размера окна на десктоп
        window.addEventListener("resize", function () {
            if (window.innerWidth >= 768) {
                mobileMenu.classList.add("hidden");
            }
        });
    }

    // Добавляем эффект параллакса для hero-секции
    const heroSection = document.querySelector(".hero-gradient");
    if (heroSection) {
        window.addEventListener("scroll", () => {
            const scrolled = window.pageYOffset;
            const parallax = heroSection.querySelector(".animate-float");
            if (parallax) {
                const speed = 0.5;
                parallax.style.transform = `translateY(${scrolled * speed}px)`;
            }
        });
    }
}

// Инициализация дополнительных функций
document.addEventListener("DOMContentLoaded", function () {
    enhanceUserExperience();

    // Добавляем индикатор прокрутки
    const scrollIndicator = document.createElement("div");
    scrollIndicator.className =
        "fixed top-0 left-0 h-1 bg-sitera-secondary z-50 transition-all duration-300";
    scrollIndicator.style.width = "0%";
    document.body.appendChild(scrollIndicator);

    window.addEventListener("scroll", () => {
        const winScroll =
            document.body.scrollTop || document.documentElement.scrollTop;
        const height =
            document.documentElement.scrollHeight -
            document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        scrollIndicator.style.width = scrolled + "%";
    });
});

// Карусель партнеров с пошаговым движением
function initPartnersCarousel() {
    const carousel = document.getElementById("partners-carousel");

    if (!carousel) {
        console.log("Карусель партнеров не найдена");
        return;
    }

    console.log("Инициализация карусели партнеров...");

    // Список партнеров с их данными
    const partners = [
        { name: "Bosch", image: "logo_Bosch_220-110.png" },
        { name: "Shure", image: "logo_Shure_220-110.png" },
        { name: "Hitachi", image: "logo_Hitachi_220-110.png" },
        { name: "Barco", image: "logo_Barco_220-110.png" },
        { name: "Crestron", image: "logo_Crestron_220-110.png" },
        { name: "Aten", image: "logo_Aten_220-110.png" },
        { name: "Smart", image: "logo_Smart_220-110.png" },
        { name: "Lumens", image: "logo_Lumens_220-110.png" },
        { name: "Vaddio", image: "logo_Vaddio_220-110.png" },
        { name: "CVS", image: "logo_CVS_220-110.png" },
        { name: "DP", image: "logo_DP_220-110.png" },
        { name: "Euromet", image: "logo_Euromet_220-110.png" },
        { name: "JPemBall", image: "logo_JPemBall_220-110.png" },
        { name: "BTech", image: "logo_BTech_220-110.png" },
        { name: "Triolion", image: "logo_Triolion_220-110.png" },
        { name: "Unilumin", image: "logo_Unilumin_220-110.png" },
        { name: "Amis", image: "logo_Amis_220-110.png" },
    ];

    // Создаем HTML для всех партнеров
    function createPartnerHTML(partner) {
        return `
            <div class="flex-shrink-0 w-48 h-24 bg-white rounded-lg shadow-md flex items-center justify-center p-4 hover:shadow-lg transition-shadow duration-300 partner-item">
                <img src="/static/images/brands/${partner.image}" alt="${partner.name}" class="max-h-full max-w-full object-contain">
            </div>
        `;
    }

    // Инициализация карусели
    function initCarousel() {
        // Создаем дубликаты для бесшовной прокрутки
        const allPartners = [...partners, ...partners];
        carousel.innerHTML = allPartners.map(createPartnerHTML).join("");

        // Добавляем стили для анимации
        const style = document.createElement("style");
        style.textContent = `
            #partners-carousel {
                transition: transform 1s ease-in-out;
            }
            .partner-item {
                margin-right: 3rem; /* space-x-12 */
            }
        `;
        document.head.appendChild(style);

        // Запускаем анимацию
        startCarousel();
    }

    let currentIndex = 0;
    let carouselInterval;

    function startCarousel() {
        carouselInterval = setInterval(() => {
            currentIndex++;

            // Если достигли конца первого набора, сбрасываем без анимации
            if (currentIndex >= partners.length) {
                // Сначала плавно доходим до последнего элемента
                carousel.style.transform = `translateX(-${
                    currentIndex * 220
                }px)`;

                setTimeout(() => {
                    // Сбрасываем в начало без анимации
                    carousel.style.transition = "none";
                    currentIndex = 0;
                    carousel.style.transform = `translateX(0)`;

                    // Возвращаем анимацию
                    setTimeout(() => {
                        carousel.style.transition = "transform 1s ease-in-out";
                    }, 50);
                }, 1000);
            } else {
                // Обычное движение
                carousel.style.transform = `translateX(-${
                    currentIndex * 220
                }px)`;
            }
        }, 1000); // Интервал 1 секунда
    }

    // Остановка карусели при наведении мыши
    carousel.addEventListener("mouseenter", () => {
        clearInterval(carouselInterval);
    });

    // Возобновление карусели при уходе мыши
    carousel.addEventListener("mouseleave", () => {
        startCarousel();
    });

    // Инициализация
    initCarousel();
}

// Эффект параллакса для hero-секции
function initParallax() {
    const parallaxElements = document.querySelectorAll(".parallax-layer");

    if (parallaxElements.length === 0) {
        console.log("Параллакс элементы не найдены");
        return;
    }

    console.log("Инициализация параллакса...");

    // Функция обновления позиции параллакса
    function updateParallax() {
        const scrolled = window.pageYOffset;
        const parallaxContainer = document.querySelector(".parallax-container");

        if (!parallaxContainer) return;

        const containerTop = parallaxContainer.offsetTop;
        const containerHeight = parallaxContainer.offsetHeight;

        // Применяем параллакс эффект только когда контейнер в видимой области
        if (scrolled < containerTop + containerHeight) {
            parallaxElements.forEach((element) => {
                const speed = element.dataset.speed || 0.5;
                const yPos = -(scrolled * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
        }
    }

    // Обработчик события скролла с оптимизацией
    let ticking = false;
    function requestTick() {
        if (!ticking) {
            window.requestAnimationFrame(updateParallax);
            ticking = true;
            setTimeout(() => {
                ticking = false;
            }, 100);
        }
    }

    // Добавляем обработчик скролла
    window.addEventListener("scroll", requestTick);

    // Инициализация при загрузке
    updateParallax();

    // Обновляем при изменении размера окна
    window.addEventListener("resize", updateParallax);
}

// Функции для работы с каталогом
function initCatalogFunctions() {
    console.log("Инициализация функций каталога...");

    // Переключение вида каталога (сетка/список)
    const viewButtons = document.querySelectorAll(".view-btn");
    const categoriesGrid = document.getElementById("categories-grid");

    console.log("Найдено кнопок вида:", viewButtons.length);
    console.log("Найдена сетка категорий:", !!categoriesGrid);

    if (viewButtons.length > 0 && categoriesGrid) {
        viewButtons.forEach((button, index) => {
            console.log(`Настройка кнопки ${index}:`, button.dataset.view);
            button.addEventListener("click", function () {
                console.log("Клик на кнопку вида:", this.dataset.view);
                const viewType = this.dataset.view;

                // Обновляем активную кнопку
                viewButtons.forEach((btn) => {
                    btn.classList.remove("bg-sitera-primary", "text-white");
                    btn.classList.add("text-gray-600");
                });

                this.classList.remove("text-gray-600");
                this.classList.add("bg-sitera-primary", "text-white");

                // Применяем вид
                if (viewType === "list") {
                    console.log("Переключение на вид списка");
                    categoriesGrid.classList.remove(
                        "grid",
                        "grid-cols-1",
                        "md:grid-cols-2",
                        "lg:grid-cols-3",
                        "xl:grid-cols-6"
                    );
                    categoriesGrid.classList.add(
                        "flex",
                        "flex-col",
                        "space-y-4"
                    );

                    // Применяем стили для вида списка
                    document
                        .querySelectorAll(".category-card")
                        .forEach((card) => {
                            card.classList.add(
                                "flex",
                                "flex-row",
                                "items-center",
                                "p-4"
                            );
                            const imageContainer =
                                card.querySelector(".relative");
                            if (imageContainer) {
                                imageContainer.classList.add(
                                    "w-24",
                                    "h-24",
                                    "mr-4"
                                );
                                imageContainer.classList.remove(
                                    "h-48",
                                    "md:h-56"
                                );
                            }
                        });
                } else {
                    console.log("Переключение на вид сетки");
                    categoriesGrid.classList.add(
                        "grid",
                        "grid-cols-1",
                        "md:grid-cols-2",
                        "lg:grid-cols-3",
                        "xl:grid-cols-6"
                    );
                    categoriesGrid.classList.remove(
                        "flex",
                        "flex-col",
                        "space-y-4"
                    );

                    // Возвращаем стили для сетки
                    document
                        .querySelectorAll(".category-card")
                        .forEach((card) => {
                            card.classList.remove(
                                "flex",
                                "flex-row",
                                "items-center",
                                "p-4"
                            );
                            const imageContainer =
                                card.querySelector(".relative");
                            if (imageContainer) {
                                imageContainer.classList.remove(
                                    "w-24",
                                    "h-24",
                                    "mr-4"
                                );
                                imageContainer.classList.add("h-48", "md:h-56");
                            }
                        });
                }
            });
        });
    }

    // Фильтры каталога
    const filterButtons = document.querySelectorAll(".filter-btn");
    console.log("Найдено кнопок фильтров:", filterButtons.length);

    filterButtons.forEach((button) => {
        button.addEventListener("click", function () {
            const filterType = this.dataset.filter;
            const isActive = this.classList.contains("bg-blue-600");

            // Сбрасываем все кнопки этого типа
            document
                .querySelectorAll(`[data-filter="${filterType}"]`)
                .forEach((btn) => {
                    btn.classList.remove("bg-sitera-primary", "text-white");
                    btn.classList.add("text-gray-600");
                });

            // Активируем нажатую кнопку
            if (!isActive) {
                this.classList.remove("text-gray-600");
                this.classList.add("bg-sitera-primary", "text-white");
            }

            applyFilters();
        });
    });

    // Сортировка
    const sortSelect = document.getElementById("sort-select");
    console.log("Найден селектор сортировки:", !!sortSelect);
    if (sortSelect) {
        sortSelect.addEventListener("change", function () {
            const sortValue = this.value;
            sortCategories(sortValue);
        });
    }

    // Фильтрация категорий в боковой панели
    const categorySearch = document.getElementById("category-search");
    const categoryItems = document.querySelectorAll(".category-item");

    if (categorySearch && categoryItems.length > 0) {
        categorySearch.addEventListener("input", function () {
            const searchTerm = this.value.toLowerCase();

            categoryItems.forEach((item) => {
                const categoryName =
                    item.querySelector("span")?.textContent.toLowerCase() || "";
                if (categoryName.includes(searchTerm)) {
                    item.style.display = "flex";
                } else {
                    item.style.display = "none";
                }
            });
        });
    }
}

function applyFilters() {
    console.log("Применение фильтров...");
    const activeFilters = {
        inStock:
            document
                .querySelector('[data-filter="in-stock"]')
                ?.classList.contains("bg-blue-600") || false,
        outOfStock:
            document
                .querySelector('[data-filter="out-of-stock"]')
                ?.classList.contains("bg-blue-600") || false,
    };

    console.log("Активные фильтры:", activeFilters);

    const categoryCards = document.querySelectorAll(".category-card");
    console.log("Найдено карточек категорий:", categoryCards.length);

    categoryCards.forEach((card) => {
        let showCard = true;

        // Применяем фильтры
        if (activeFilters.inStock && !activeFilters.outOfStock) {
            // Показывать только в наличии
            const inStock = card.querySelector(".text-green-600");
            showCard = !!inStock;
        } else if (!activeFilters.inStock && activeFilters.outOfStock) {
            // Показывать только отсутствующие
            const outOfStock = card.querySelector(".text-red-600");
            showCard = !!outOfStock;
        }

        card.style.display = showCard ? "block" : "none";
    });
}

function sortCategories(sortBy) {
    console.log("Сортировка категорий по:", sortBy);
    const categoriesGrid = document.getElementById("categories-grid");
    if (!categoriesGrid) {
        console.log("Сетка категорий не найдена");
        return;
    }

    const categoryCards = Array.from(
        categoriesGrid.querySelectorAll(".category-card")
    );
    console.log("Найдено карточек для сортировки:", categoryCards.length);

    categoryCards.sort((a, b) => {
        switch (sortBy) {
            case "name":
                const titleA = a.querySelector("h3")?.textContent.trim() || "";
                const titleB = b.querySelector("h3")?.textContent.trim() || "";
                return titleA.localeCompare(titleB);
            case "popular":
                // Сортировка по количеству товаров (в обратном порядке)
                const countA =
                    parseInt(
                        a.querySelector(".category-badge span")?.textContent
                    ) || 0;
                const countB =
                    parseInt(
                        b.querySelector(".category-badge span")?.textContent
                    ) || 0;
                return countB - countA;
            case "newest":
                // Здесь можно добавить логику сортировки по дате
                return 0;
            default:
                return 0;
        }
    });

    // Перестраиваем DOM
    categoryCards.forEach((card) => {
        categoriesGrid.appendChild(card);
    });
}

// Экспорт функций для глобального доступа
window.Sitera = {
    smoothScrollTo,
    showMessage,
    animateCounter,
    enhanceUserExperience,
    initPartnersCarousel,
    initParallax,
    initCatalogFunctions,
    applyFilters,
    sortCategories,
};
