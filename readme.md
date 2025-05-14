# Documentación de la API

Este directorio contiene los archivos relacionados con la API del proyecto, que proporciona funcionalidades para manejar chats, embeddings y la gestión de archivos utilizando arquitectura RAG.

## Archivos Principales

- **chat.py**: Proporciona un endpoint para interactuar con un agente de chat. Permite hacer preguntas al agente y seguir conversaciones mediante un `thread_id`.
- **embedding.py**: Ofrece endpoints para crear y eliminar embeddings de documentos. Utiliza configuraciones específicas para dividir documentos y generar embeddings que se almacenan en una base de datos vectorial.
- **uploads.py**: Gestiona la subida, eliminación y verificación de archivos. También permite la generación de embeddings al subir archivos.

## Requisitos

- Docker
- Docker Compose

## Instalación

1. Asegúrate de tener Docker y Docker Compose instalados en tu sistema.
2. Navega al directorio donde se encuentra el archivo `docker-compose-mogo.yml`.
3. Ejecuta el siguiente comando para levantar los servicios:

   ```bash
   docker-compose -f docker-compose-mogo.yml up --build
   ```

   Este comando construirá las imágenes necesarias y levantará los contenedores definidos en el archivo `docker-compose-mogo.yml`.

4. Una vez que los servicios estén en funcionamiento, la API estará disponible en `http://localhost:8010`.

## Uso

### Endpoints Principales

#### Chat

- **POST /chats/ask/{file_name}**: Permite hacer preguntas al agente. Si se proporciona un `thread_id`, se sigue la conversación existente.

#### Embeddings

- **POST /embeddings/{file_name}**: Crea embeddings para un archivo específico.
- **DELETE /embeddings/{file_name}**: Elimina los embeddings asociados a un archivo.

#### Archivos

- **GET /files/**: Lista archivos con soporte de paginación y filtrado.
- **POST /files/upload**: Sube un archivo al servidor.
- **DELETE /files/{file_name}**: Elimina un archivo del servidor.
- **GET /files/exist/{file_name}**: Verifica si un archivo existe en el servidor.
- **POST /files/upload/embeddings**: Sube un archivo y genera embeddings automáticamente.

## Contribuciones

Si deseas contribuir, por favor sigue las siguientes pautas:

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit de ellos (`git commit -am 'Añadir nueva funcionalidad'`).
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

## Licencia

Este proyecto está bajo la Licencia MIT