/**
 * 主 JavaScript 文件
 * 处理滚动动画、平滑滚动等交互效果
 */

// 等待 DOM 加载完成
document.addEventListener('DOMContentLoaded', () => {
  // 初始化滚动动画
  initScrollAnimations();

  // 初始化平滑滚动
  initSmoothScroll();

  // 初始化移动端菜单
  initMobileMenu();

  // 初始化卡片点击
  initCardClick();
});

/**
 * 滚动动画 - 使用 Intersection Observer
 */
function initScrollAnimations() {
  const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        // 动画只播放一次，停止观察
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // 观察所有带有 fade-in 类的元素
  document.querySelectorAll('.fade-in').forEach(el => {
    observer.observe(el);
  });
}

/**
 * 平滑滚动 - 锚点跳转
 */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;

      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        e.preventDefault();
        const headerOffset = 80; // 考虑固定导航栏的高度
        const elementPosition = targetElement.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });

        // 如果是移动端菜单，点击后关闭菜单
        if (window.innerWidth <= 768) {
          const menuToggle = document.getElementById('menuToggle');
          const headerNav = document.getElementById('headerNav');
          if (menuToggle && headerNav) {
            menuToggle.classList.remove('active');
            headerNav.classList.remove('active');
          }
        }
      }
    });
  });
}

/**
 * 移动端菜单
 */
function initMobileMenu() {
  const menuToggle = document.getElementById('menuToggle');
  const headerNav = document.getElementById('headerNav');

  if (menuToggle && headerNav) {
    menuToggle.addEventListener('click', () => {
      menuToggle.classList.toggle('active');
      headerNav.classList.toggle('active');
    });

    // 点击导航外部关闭菜单
    document.addEventListener('click', (e) => {
      if (!menuToggle.contains(e.target) && !headerNav.contains(e.target)) {
        menuToggle.classList.remove('active');
        headerNav.classList.remove('active');
      }
    });
  }
}

/**
 * 图片懒加载（可选增强）
 */
function initLazyLoading() {
  const images = document.querySelectorAll('img[data-src]');

  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
        imageObserver.unobserve(img);
      }
    });
  });

  images.forEach(img => imageObserver.observe(img));
}

/**
 * 卡片点击跳转 - 整个卡片可点击，但排除标签等内部元素
 */
function initCardClick() {
  // 处理普通卡片 (.card)
  document.querySelectorAll('.card[data-url]').forEach(card => {
    card.addEventListener('click', (e) => {
      // 如果点击的是标签或其他带有 data-no-click 的元素，不跳转
      if (e.target.closest('[data-no-click]')) {
        return;
      }
      // 跳转到文章页面
      window.location.href = card.dataset.url;
    });
  });

  // 处理大卡片 (.article-card-large)
  document.querySelectorAll('.article-card-large[data-url]').forEach(card => {
    card.addEventListener('click', (e) => {
      if (e.target.closest('[data-no-click]')) {
        return;
      }
      window.location.href = card.dataset.url;
    });
  });
}
