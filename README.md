# TravelSphere ✦

Prototipo de planificación de viajes en Streamlit con interfaz Cyber-Luxe / Glassmorphism, modo oscuro, pestañas funcionales, filtros, enlaces a proveedores externos, visualización financiera Plotly y exportación CSV.

## Requisitos
- Python 3.10 o superior
- pip

## Ejecutar localmente
```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en Streamlit Community Cloud
1. Crea un repositorio en GitHub y sube el contenido de esta carpeta.
2. En [share.streamlit.io](https://share.streamlit.io/), conecta GitHub.
3. Selecciona el repositorio, la rama y `app.py` como archivo principal.
4. Pulsa **Deploy**. No se requieren secretos para esta demo.

## Estructura
```text
TravelSphere/
├── app.py                     # Interfaz y flujo principal
├── travelsphere/
│   ├── __init__.py
│   ├── data.py                 # Datos de demostración / punto de integración API
│   └── utils.py                # Formato de moneda, fechas y URLs
├── .streamlit/config.toml      # Tema oscuro
├── requirements.txt
├── .gitignore
└── README.md
```

## Importante antes de producción
- Las tarifas, puntuaciones, hoteles, restaurantes y actividades son datos de demostración; no son resultados en tiempo real ni recomendaciones verificadas.
- Los botones abren búsquedas en servicios externos; no completan compras ni garantizan disponibilidad.
- Para precios y disponibilidad reales, integra APIs autorizadas de vuelos, alojamiento y actividades. Respeta términos de uso, atribución, límites y condiciones comerciales de cada proveedor.
- Guarda credenciales en **Streamlit Secrets** (`.streamlit/secrets.toml` local, excluido de Git) o en secretos de Community Cloud. Nunca subas claves al repositorio.
- Antes de operar con datos reales, añade validación de datos, pruebas, manejo de errores de API, observabilidad y avisos de privacidad.
- Las conversiones USD/EUR son aproximaciones estáticas de demostración; reemplázalas por un tipo de cambio actualizado si necesitas conversiones fiables.

## Personalización
- Ajusta el estilo CSS incluido en `app.py`.
- Sustituye `build_demo_results()` en `travelsphere/data.py` por funciones de servicio conectadas a proveedores autorizados.
- Añade tests y un archivo de bloqueo de dependencias para despliegues reproducibles.


## Conectar proveedores de datos

La aplicación permite elegir **Demostración** o **APIs conectadas**. Sin credenciales, las pantallas siguen funcionando con datos de ejemplo; no se hacen llamadas externas.

### Amadeus (vuelos y hoteles)

1. Crea credenciales en [Amadeus for Developers](https://developers.amadeus.com/).
2. Añade estas variables a `.streamlit/secrets.toml` en local o a **App settings → Secrets** en Streamlit Community Cloud:

```toml
AMADEUS_CLIENT_ID = "tu_client_id"
AMADEUS_CLIENT_SECRET = "tu_client_secret"
AMADEUS_BASE_URL = "https://test.api.amadeus.com"
```

El entorno de pruebas puede devolver datos limitados o de prueba. Usa la URL de producción únicamente con credenciales de producción habilitadas por Amadeus.

### Google Places (restaurantes)

Activa Places API (New) en tu proyecto de Google Cloud y añade:

```toml
GOOGLE_PLACES_API_KEY = "tu_api_key"
```

Restringe la clave por API y, cuando corresponda, por aplicación. Google Places no proporciona necesariamente precios de menú; en ese caso TravelSphere muestra **Precio no disponible** en vez de inventar un costo.

### Comportamiento y límites

- Cada proveedor es opcional y se consulta solo si eliges **APIs conectadas** y sus credenciales están configuradas.
- Si una consulta falla o no devuelve resultados, la aplicación muestra un aviso y conserva los datos de demostración para esa sección.
- Los resultados de proveedores están sujetos a cobertura, límites, permisos y condiciones de cada API. Confirma siempre la oferta y disponibilidad en el proveedor.
- Las cifras del resumen financiero y el itinerario siguen siendo estimaciones de demostración; no son una cotización integral del viaje.
- No guardes credenciales en Git. `.streamlit/secrets.toml` está excluido mediante `.gitignore`.
