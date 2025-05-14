from langchain_core.tools import tool

# Definir funcion que sera llamada
# tool


@tool
def create_appointment(
    date: str,
    time: str,
    location: str,
    description: str = "",
) -> str:
    """
    Recibe una fecha y un descripción y crea una cita en el calendario.
    Args:
        date (str): Fecha de la cita.
        time (str): Hora de la cita.
        location (str): Ubicación de la cita.
        description (str, optional): Descripción de la cita. Defaults to "".    
    """
    # Aquí iría la lógica para crear la cita en el calendario
    return f"Cita creada para el {date} a las {time} en {location}. Descripción: {description}"
