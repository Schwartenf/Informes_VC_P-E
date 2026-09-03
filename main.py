from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Template
from xhtml2pdf import pisa
import base64
import os
import io

app = FastAPI(title="Servicio de Generación de Informes Técnicos")

# Montar archivos estáticos (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def ruta_principal():
    return FileResponse("static/index.html")

async def convertir_a_base64(archivo: UploadFile):
    if not archivo or not archivo.filename:
        return None
    contenido = await archivo.read()
    if not contenido:
        return None
    return base64.b64encode(contenido).decode("utf-8")

@app.post("/generar-informe")
async def generar_informe(
    numero: str = Form("INF-001"),
    fecha_emision: str = Form(...),
    fecha_visita: str = Form(...),
    cliente: str = Form(...),
    ruc: str = Form(...),
    direccion: str = Form(...),
    area_visita: str = Form(...),
    tecnico: str = Form(...),
    supervisor: str = Form(...),
    introduccion: str = Form(...),
    solucion: str = Form(...),
    propuesta: str = Form(...),
    caption1: str = Form(""),
    caption2: str = Form(""),
    foto1: UploadFile = File(None),
    foto2: UploadFile = File(None)
):
    b64_foto1 = await convertir_a_base64(foto1)
    b64_foto2 = await convertir_a_base64(foto2)

    ruta_plantilla = os.path.join("templates", "plantilla_pdf.html")
    with open(ruta_plantilla, "r", encoding="utf-8") as f:
        plantilla_contenido = f.read()

    template = Template(plantilla_contenido)
    html_procesado = template.render(
        numero=numero,
        fecha_emision=fecha_emision,
        fecha_visita=fecha_visita,
        cliente=cliente,
        ruc=ruc,
        direccion=direccion,
        area_visita=area_visita,
        tecnico=tecnico,
        supervisor=supervisor,
        introduccion=introduccion,
        solucion=solucion,
        propuesta=propuesta,
        caption1=caption1 or "Evidencia 1",
        caption2=caption2 or "Evidencia 2",
        foto1_base64=b64_foto1,
        foto2_base64=b64_foto2
    )

    # Conversión a PDF mediante xhtml2pdf en memoria
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html_procesado), dest=pdf_buffer)

    if pisa_status.err:
        return Response(content="Error interno al compilar el PDF", status_code=500)

    pdf_bytes = pdf_buffer.getvalue()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="Informe_{numero}.pdf"'}
    )