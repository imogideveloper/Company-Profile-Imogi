/**
* Template Name: Presento
* Template URL: https://bootstrapmade.com/presento-bootstrap-corporate-template/
* Updated: Aug 07 2024 with Bootstrap v5.3.3
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/

(function() {
  "use strict";

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled() {
    const selectBody = document.querySelector('body');
    const selectHeader = document.querySelector('#header');
    if (!selectHeader.classList.contains('scroll-up-sticky') && !selectHeader.classList.contains('sticky-top') && !selectHeader.classList.contains('fixed-top')) return;
    window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
  }

  document.addEventListener('scroll', toggleScrolled);
  window.addEventListener('load', toggleScrolled);

  /**
   * Mobile nav toggle
   */
  const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');

  function mobileNavToogle() {
    document.querySelector('body').classList.toggle('mobile-nav-active');
    mobileNavToggleBtn.classList.toggle('bi-list');
    mobileNavToggleBtn.classList.toggle('bi-x');
  }
  mobileNavToggleBtn.addEventListener('click', mobileNavToogle);

  /**
   * Hide mobile nav on same-page/hash links
   */
  document.querySelectorAll('#navmenu a').forEach(navmenu => {
    navmenu.addEventListener('click', () => {
      if (document.querySelector('.mobile-nav-active')) {
        mobileNavToogle();
      }
    });

  });

  /**
   * Toggle mobile nav dropdowns
   */
  document.querySelectorAll('.navmenu .toggle-dropdown').forEach(navmenu => {
    navmenu.addEventListener('click', function(e) {
      e.preventDefault();
      this.parentNode.classList.toggle('active');
      this.parentNode.nextElementSibling.classList.toggle('dropdown-active');
      e.stopImmediatePropagation();
    });
  });

  /**
   * Scroll top button
   */
  let scrollTop = document.querySelector('.scroll-top');

  function toggleScrollTop() {
    if (scrollTop) {
      window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
    }
  }
  if (scrollTop) {
    scrollTop.addEventListener('click', (e) => {
      e.preventDefault();
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }

  window.addEventListener('load', toggleScrollTop);
  document.addEventListener('scroll', toggleScrollTop);

  /**
   * Animation on scroll function and init
   */
  function aosInit() {
    AOS.init({
      duration: 600,
      easing: 'ease-in-out',
      once: true,
      mirror: false
    });
  }
  window.addEventListener('load', aosInit);

  /**
   * Initiate glightbox
   */
  const glightbox = GLightbox({
    selector: '.glightbox'
  });

  /**
   * Init swiper sliders
   */
  function initSwiper() {
    document.querySelectorAll(".init-swiper").forEach(function(swiperElement) {
      let config = JSON.parse(
        swiperElement.querySelector(".swiper-config").innerHTML.trim()
      );

      if (swiperElement.classList.contains("swiper-tab")) {
        initSwiperWithCustomPagination(swiperElement, config);
      } else {
        new Swiper(swiperElement, config);
      }
    });
  }

  window.addEventListener("load", initSwiper);

  /**
   * Initiate Pure Counter
   */
  new PureCounter();

  /**
   * Init isotope layout and filters
   */
  document.querySelectorAll('.isotope-layout').forEach(function(isotopeItem) {
    let layout = isotopeItem.getAttribute('data-layout') ?? 'masonry';
    let filter = isotopeItem.getAttribute('data-default-filter') ?? '*';
    let sort = isotopeItem.getAttribute('data-sort') ?? 'original-order';

    let initIsotope;
    imagesLoaded(isotopeItem.querySelector('.isotope-container'), function() {
      initIsotope = new Isotope(isotopeItem.querySelector('.isotope-container'), {
        itemSelector: '.isotope-item',
        layoutMode: layout,
        filter: filter,
        sortBy: sort
      });
    });

    isotopeItem.querySelectorAll('.isotope-filters li').forEach(function(filters) {
      filters.addEventListener('click', function() {
        isotopeItem.querySelector('.isotope-filters .filter-active').classList.remove('filter-active');
        this.classList.add('filter-active');
        initIsotope.arrange({
          filter: this.getAttribute('data-filter')
        });
        if (typeof aosInit === 'function') {
          aosInit();
        }
      }, false);
    });

  });

  /**
   * Frequently Asked Questions Toggle
   */
  document.querySelectorAll('.faq-item h3, .faq-item .faq-toggle').forEach((faqItem) => {
    faqItem.addEventListener('click', () => {
      faqItem.parentNode.classList.toggle('faq-active');
    });
  });

  /**
   * Navmenu Scrollspy
   */
  let navmenulinks = document.querySelectorAll('.navmenu a');

  function navmenuScrollspy() {
    navmenulinks.forEach(navmenulink => {
      if (!navmenulink.hash) return;
      let section = document.querySelector(navmenulink.hash);
      if (!section) return;
      let position = window.scrollY + 200;
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        document.querySelectorAll('.navmenu a.active').forEach(link => link.classList.remove('active'));
        navmenulink.classList.add('active');
      } else {
        navmenulink.classList.remove('active');
      }
    });
  }
  window.addEventListener('load', navmenuScrollspy);
  document.addEventListener('scroll', navmenuScrollspy);

})();

/**
 * Animated Testimonials (tumpukan foto + teks bergiliran, autoplay)
 */
(function() {
  const root = document.querySelector('#atestimonials');
  if (!root) return;

  const photos = Array.from(root.querySelectorAll('.atestimonial-photo'));
  const slides = Array.from(root.querySelectorAll('.atestimonial-slide'));
  const total = photos.length;
  if (!total) return;

  const rotations = [-7, 6, -5, 8, -6, 5];
  let active = 0;
  let timer = null;

  function render() {
    photos.forEach((img, i) => {
      const isActive = i === active;
      img.style.zIndex = isActive ? total : total - Math.abs(i - active);
      img.style.opacity = isActive ? '1' : '0.35';
      img.style.transform = isActive ?
        'translateY(0) scale(1) rotate(0deg)' :
        'translateY(14px) scale(0.92) rotate(' + rotations[i % rotations.length] + 'deg)';
    });
    slides.forEach((s, i) => s.classList.toggle('is-active', i === active));
  }

  function go(step) {
    active = (active + step + total) % total;
    render();
  }

  function startAutoplay() {
    clearInterval(timer);
    timer = setInterval(() => go(1), 5000);
  }

  root.querySelectorAll('.atestimonial-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      go(btn.dataset.dir === 'prev' ? -1 : 1);
      startAutoplay();
    });
  });

  render();
  startAutoplay();
})();

/**
 * Tabel Perbandingan -> di HP dibangun jadi kartu per-ERP (tanpa scroll samping).
 * Kartu dibaca otomatis dari tabel (satu sumber data), ERPNext ditaruh paling atas.
 */
(function() {
  const table = document.querySelector('.compare-table');
  const container = document.querySelector('.compare-cards');
  if (!table || !container || container.children.length) return;

  const heads = table.querySelectorAll('thead th');
  const cols = [];
  for (let i = 1; i < heads.length; i++) {
    const th = heads[i];
    const nameEl = th.querySelector('.cmp-name');
    const iconEl = th.querySelector('.cmp-icon');
    cols.push({
      index: i,
      name: nameEl ? nameEl.textContent.trim() : th.textContent.trim(),
      icon: iconEl ? iconEl.outerHTML : '',
      highlight: th.classList.contains('cmp-highlight'),
    });
  }
  // ERPNext (highlight) di urutan pertama
  cols.sort((a, b) => (b.highlight ? 1 : 0) - (a.highlight ? 1 : 0));

  const rows = table.querySelectorAll('tbody tr');
  cols.forEach((col) => {
    const card = document.createElement('div');
    card.className = 'compare-card' + (col.highlight ? ' is-highlight' : '');
    let html = '<div class="compare-card-head">';
    if (col.highlight) html += '<span class="compare-card-badge"><i class="bi bi-star-fill"></i> Rekomendasi</span>';
    html += col.icon + '<span class="compare-card-name">' + col.name + '</span></div>';
    html += '<div class="compare-card-rows">';
    rows.forEach((tr) => {
      const cells = tr.children;
      const feature = cells[0] ? cells[0].textContent.trim() : '';
      const val = cells[col.index] ? cells[col.index].innerHTML.trim() : '';
      html += '<div class="compare-card-row"><span class="ccr-feature">' + feature +
        '</span><span class="ccr-val">' + val + '</span></div>';
    });
    html += '</div>';
    card.innerHTML = html;
    container.appendChild(card);
  });
})();

/**
 * Solusi ERPNext: tab switcher (pilih industri -> tampil panelnya)
 */
(function() {
  const tabs = document.querySelectorAll('.solusi-tab');
  if (!tabs.length) return;

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const target = document.getElementById(tab.dataset.target);
      if (!target) return;
      document.querySelectorAll('.solusi-tab').forEach((t) => t.classList.remove('active'));
      document.querySelectorAll('.solusi-panel').forEach((p) => p.classList.remove('active'));
      tab.classList.add('active');
      target.classList.add('active');
    });
  });
})();

/**
 * Klien Kami: marquee CSS anti-macet — gandakan logo secukupnya lalu jalan terus
 * dengan kecepatan tetap, berapa pun jumlah logo aktif (tak bergantung Swiper).
 */
(function() {
  const marquee = document.querySelector('.clients-marquee');
  if (!marquee) return;
  const track = marquee.querySelector('.clients-track');
  if (!track || !track.children.length) return;

  const SPEED = 60; // piksel per detik
  const baseHTML = track.innerHTML;

  function build() {
    track.innerHTML = baseHTML;
    // gandakan hingga cukup lebar (>= 2x layar) & jumlah set genap agar mulus
    let sets = 1;
    while ((track.scrollWidth < marquee.clientWidth * 2 || sets % 2 !== 0) && sets < 40) {
      track.insertAdjacentHTML('beforeend', baseHTML);
      sets++;
    }
    const half = track.scrollWidth / 2;
    track.style.setProperty('--marquee-shift', half + 'px');
    track.style.animationDuration = (half / SPEED) + 's';
  }

  window.addEventListener('load', build); // setelah gambar termuat -> lebar akurat
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(build, 200);
  });
})();

/**
 * Ring produk: sebar ikon produk merata mengelilingi logo IMOGI.
 * Posisi dihitung dari jumlah produk & ukuran ring (responsif).
 */
(function() {
  const ring = document.querySelector('.product-ring');
  if (!ring) return;
  const rotor = ring.querySelector('.product-ring-rotor');
  const items = rotor ? Array.from(rotor.querySelectorAll('.product-ring-item')) : [];
  if (!items.length) return;

  function layout() {
    const size = ring.clientWidth;
    const itemSize = items[0].offsetWidth || 88;
    const radius = size / 2 - itemSize / 2 - 8; // jarak dari tepi
    const n = items.length;

    // lapisan garis penghubung pusat -> produk
    let spokes = rotor.querySelector('.product-ring-spokes');
    if (!spokes) {
      spokes = document.createElement('div');
      spokes.className = 'product-ring-spokes';
      rotor.insertBefore(spokes, rotor.firstChild); // di belakang ikon
    }
    spokes.innerHTML = '';

    items.forEach((el, i) => {
      const angle = (2 * Math.PI / n) * i - Math.PI / 2; // mulai dari atas
      const x = size / 2 + radius * Math.cos(angle) - itemSize / 2;
      const y = size / 2 + radius * Math.sin(angle) - itemSize / 2;
      el.style.left = x + 'px';
      el.style.top = y + 'px';

      const spoke = document.createElement('span');
      spoke.className = 'pri-spoke';
      spoke.style.left = (size / 2) + 'px';
      spoke.style.top = (size / 2) + 'px';
      spoke.style.width = radius + 'px';
      spoke.style.transform = 'rotate(' + (angle * 180 / Math.PI) + 'deg)';
      spoke.style.setProperty('--spoke-i', i); // giliran animasi cahaya
      spokes.appendChild(spoke);
    });
  }

  layout();
  window.addEventListener('load', layout);
  let t;
  window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(layout, 150); });
})();

/**
 * Karakter 3D: berjalan masuk dari kiri saat ring/section terlihat.
 */
(function() {
  const mascot = document.querySelector('.product-mascot');
  if (!mascot) return;
  const video = mascot.querySelector('video');

  const trigger = () => {
    mascot.classList.add('walk-in');
    if (video) {
      video.muted = true; // wajib agar autoplay diizinkan browser
      const p = video.play();
      if (p && p.catch) p.catch(() => {});
    }
  };

  if (!('IntersectionObserver' in window)) { trigger(); return; }

  const io = new IntersectionObserver((entries, obs) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { trigger(); obs.disconnect(); }
    });
  }, { threshold: 0.35 });

  io.observe(mascot);
})();