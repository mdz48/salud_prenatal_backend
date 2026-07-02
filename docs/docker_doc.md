# Esta es información para el despliegue de los contenedores y comandos útiles para el despliegue y logs.

- **Para ejecutar los contenedores**:

  ```bash
  docker compose up -d 
  ```

- **Para detener los contenedores**:

  ```bash
  docker compose down
  ```

- **Para ver los logs de los contenedores**:

  ```bash
  docker compose logs -f
  ```

-  **Constuir una imagen con lo mas reciente**:

    ```bash
    docker compose up -d --build backend
    ```
