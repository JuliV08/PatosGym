# PatosGym - Arquitectura del Proyecto (Guía para Agentes IA)

Este documento detalla la estructura, el stack tecnológico y las convenciones de UI/UX del proyecto **PatosGym**, diseñado para que otro agente de Inteligencia Artificial pueda comprender el contexto y colaborar de manera efectiva.

---

## 🏗️ 1. Descripción General y Tech Stack
PatosGym es una aplicación web monolítica (Server-Side Rendering) construida para un gimnasio en Villa Lugano. Su objetivo es presentar las instalaciones, el equipo de profesores y la propuesta de valor del gimnasio con un diseño catalogado como "Ultra Premium".

**Stack Tecnológico:**
- **Backend Framework:** Django (Python).
- **Base de Datos:** PostgreSQL (configurable vía variables de entorno).
- **Frontend / Styling:** Vanilla HTML/Django Templates + **Tailwind CSS** (vía CDN local/script). NO se usa Bootstrap.
- **Interactividad (Frontend):** Vanilla Javascript + Bibliotecas específicas:
  - **Swiper.js** (v11) para carruseles (Equipo, Hero, Testimonios).
  - **GLightbox** para visualización de galerías.
- **Procesamiento de Imágenes:** `django-imagekit` para generación automática de miniaturas en el backend.

---

## 📁 2. Estructura del Repositorio (Apps de Django)

El proyecto está dividido en aplicaciones modulares:

### `patosgym_project/` (Directorio Principal)
Contiene la configuración global.
- Usa enrutamiento principal (`urls.py`).
- Los settings están divididos (`settings/base.py`, `settings/development.py`, `settings/production.py`) y utilizan `python-decouple` para cargar variables de entorno desde un `.env`.

### `landing/` (App Principal del Frontend)
Maneja la vista de la página principal (`home_view`) y el contenido dinámico asociado.
- **`HeroImage` (Model):** Gestiona las imágenes dinámicas del carrusel principal. Campos principales: `imagen`, `titulo`, `orden`, `activo`.
- **`TeamMember` (Model):** Gestiona los perfiles del staff. Campos principales: `nombre`, `puesto` (ej: Personal Trainer, Dueño), `puesto_secundario` (opcional), `foto`, `cv_info` (descripción), `video_url` (YouTube embed automático) y `orden`.

### `gallery/` (App de Galería)
Maneja las imágenes de las instalaciones del gimnasio.
- **`GalleryPhoto` (Model):** Tiene validadores de tamaño (max 20MB) y sanitización de nombres de archivo.
  - Campos: `image` (original), `thumbnail` (generado por `ImageSpecField`), `category` (Vestuarios, Cardio, Musculación, etc.), `title`, `alt_text`, `is_active`, `sort_order`.

---

## 🎨 3. Convenciones de Diseño UI/UX (¡MUY IMPORTANTE!)

El requerimiento histórico principal del usuario es que el diseño debe ser **"Ultra Premium, Moderno y Atractivo"**. Si agregas componentes nuevos, DEBEN seguir estas pautas:

### Paleta de Colores
- **Fondo General:** Dark theme profundo (`bg-pg-black` -> `#0a0a0a` y `#1a1a1a`).
- **Acento (Primario):** Naranja PatosGym (`pg-orange` -> `#F97316`).
- **Acento Secundario:** Ámbar (`pg-amber` -> `#F59E0B`).
- *Regla:* Nunca usar colores básicos por defecto de Tailwind sin justificación. Usar gradientes donde aplique (`bg-gradient-to-r from-pg-orange to-amber-500`).

### Estilo de Componentes (Glassmorphism & Shadows)
El proyecto hace un uso ultraintensivo de efectos "Glass" (vidrio esmerilado).
- **Fondo de Tarjetas:** En lugar de fondos sólidos, usa `bg-black/60 backdrop-blur-xl`.
- **Bordes:** Finos y semi-transparentes (`border border-white/20`), que en `:hover` cambian a `border-pg-orange/60`.
- **Sombras (Shadows):** Sombras profundas en reposo (`shadow-2xl shadow-black/50`) que brillan en hover (`hover:shadow-pg-orange/40`).
- **Bordes Redondeados:** `rounded-2xl` o `rounded-3xl` para componentes principales. No usar esquinas rectas.

### Elementos Interactivos
- **Botones y Flechas:** Deben tener transiciones suaves (`transition-all duration-300`). En `:hover` deben escalar suavemente (`hover:scale-105`) o cambiar opacidades.
- **Iconos:** Se usan SVGs in-line limpios (`stroke`, no `fill` masivos), generalmente animados en hover (ej: `group-hover:translate-x-1`). Evita insertar SVGs inyectados automáticamente por librerías (ej: Swiper).
- **Cursor Personalizado:** El sitio tiene un cursor CSS personalizado con un "trail" naranja (`.cursor-dot` y `.cursor-ring`).

---

## 💡 4. Vistas y Templates Existentes

El renderizado principal ocurre en `landing/views.py -> home_view`.
Esta vista pasa los objetos iterables al template `templates/landing/home.html`, el cual está compuesto por múltiples "partials" (fragmentos de HTML) mediante `{% include %}`:

1. `partials/hero.html`
2. `partials/features.html`
3. `partials/about.html`
4. `partials/gallery.html` (Usa `GalleryPhoto`)
5. `partials/team.html` (Carrusel con modal de video embebido, usa `TeamMember`)
6. `partials/pricing.html`
7. `partials/testimonials.html`
8. `partials/contact.html`

El esqueleto HTML principal con las importaciones de Tailwind, tipografías (Google Font: *Inter*) y CSS global está en `templates/landing/base.html`.

---

## ⚠️ 5. Bugs Conocidos / "Gotchas" Recientes
A modo de historial para el otro agente, acá hay cosas solucionadas recientemente para no volver a cometer los mismos errores:
- **Navegación de Swiper:** Swiper.js inyecta SVGs feos por defecto si usas las clases `swiper-button-next`/`prev`. Para flechas premium, se usan clases custom como `team-nav-next` y se referencian explícitamente en el objeto de configuración JS de Swiper.
- **Configuración de variables de entorno:** Al correr scripts sueltos, puede fallar si no se declara `DJANGO_SETTINGS_MODULE="patosgym_project.settings.development"`.
- **Sintaxis de Templates y Saltos de Línea:** Evitar usar secuencias de escape literales (`\n`) dentro del código HTML o generar saltos de línea extraños dentro de etiquetas `{{ }}` que rompen el motor de parsing de Django causando que el código literal ("{{ object.method }}") aparezca renderizado en la interfaz.

---

Este documento te otorga todo el contexto técnico y visual del proyecto PatosGym. Estás listo para solicitar creaciones, refactorizaciones o agregar endpoints manteniendo la estética y estándar arquitectónico del proyecto.
