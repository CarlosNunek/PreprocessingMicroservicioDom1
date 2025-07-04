from flask import Flask, jsonify
import requests
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)  # Habilita CORS

# Funciones auxiliares
def estandarizar_categoria(categoria):
    categorias = {"baja": 0, "media": 1, "alta": 2}
    return categorias.get(categoria.lower(), -1)

def normalizar_puntuacion(p, maximo): return round(p / maximo, 2)
def normalizar_edad(edad, min_, max_): return round((edad - min_) / (max_ - min_), 2)
def eliminar_duplicados(lista): return list(set(lista))

@app.route("/api/preprocesar_datos/<cedula>", methods=["GET"])
@cross_origin()
def preprocesar_datos(cedula):
    try:
        print(f"[✓] Recibida solicitud de preprocesamiento para: {cedula}")

        user_url = f"http://localhost:5000/api/reclusos/{cedula}"
        eval_url = f"http://localhost:5003/api/evaluacion/{cedula}"
        send_url = "http://localhost:5006/api/enviar_evento"

        print(f"Obteniendo usuario desde: {user_url}")
        usuario = requests.get(user_url).json()
        print("Datos usuario:", usuario)

        print(f"Obteniendo evaluación desde: {eval_url}")
        evaluacion = requests.get(eval_url).json()
        print("Datos evaluación:", evaluacion)

        resultado = {
            "id_recluso": cedula,
            "nombre": usuario.get("nombre", ""),
            "edad": normalizar_edad(usuario.get("edad", 0), 18, 100),
            "nivel_agresividad": evaluacion.get("nivel_agresividad", 0),
            "puntaje_psicologico": normalizar_puntuacion(evaluacion.get("puntaje_psicologico", 0), 100),
            "tiempo_encarcelado": normalizar_puntuacion(evaluacion.get("tiempo_encarcelado", 0), 100),
            "riesgo_reincidencia": normalizar_puntuacion(evaluacion.get("riesgo_reincidencia", 0), 10),
            "trastornos": eliminar_duplicados(evaluacion.get("trastornos", []))
        }

        print("Datos normalizados:", resultado)
        response = requests.post(send_url, json=resultado)

        if response.status_code != 201:
            print("[!] Error al enviar a Kafka:", response.text)
            return jsonify({"error": "Fallo al enviar evento"}), 500

        print("[✓] Evento enviado a Kafka")
        return jsonify({"mensaje": "Preprocesado y enviado", "datos": resultado}), 200

    except Exception as e:
        print("[!] Error en preprocesamiento:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5004)
