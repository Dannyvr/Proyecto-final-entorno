# Subsistema de Generación de Entorno

## Introducción

### Contexto General del Proyecto

El presente proyecto se enmarca en el desarrollo de una simulación de una colonia de hormigas, un sistema complejo dividido en cinco subsistemas modulares que interactúan entre sí. El propósito fundamental de este ejercicio es aplicar y evidenciar prácticas avanzadas de calidad de software, utilizando la metodología de Desarrollo Guiado por Pruebas (Test-Driven Development - TDD) como pilar para asegurar la robustez, mantenibilidad y fiabilidad de cada componente y del sistema en su conjunto.

### Contexto del Subsistema Asignado

Dentro de este ecosistema, al Grupo #4 se le ha asignado la responsabilidad de diseñar e implementar el **Subsistema de Generación de Entorno**. Este componente actúa como el "mundo" o el "tablero de juego" de la simulación. Su función principal es crear, gestionar y mantener el estado de todos los elementos con los que las hormigas interactuarán, lo que incluye las zonas del mapa, los recursos (alimentos) y las amenazas (enemigos).

### Objetivos del Subsistema

Para cumplir con su rol de manera efectiva, el Subsistema de Generación de Entorno se centrará en los siguientes objetivos clave:

- **Modelar un Entorno Dinámico**: Definir y administrar las entidades del mundo, como zonas, recursos y amenazas, controlando su ciclo de vida desde la creación hasta su eliminación.
- **Exponer una API Robusta**: Proveer una interfaz de programación de aplicaciones (API) clara, consistente y bien documentada. Esta API permitirá a los otros subsistemas (como Recolección y Defensa) consultar el estado del mundo y notificar cambios de manera controlada.
- **Garantizar la Calidad a través de TDD**: Implementar el 100% de la funcionalidad siguiendo un estricto ciclo de TDD (Rojo-Verde-Refactor), asegurando una alta cobertura de pruebas (>80%) y un diseño de código limpio y desacoplado.

## Tareas del Entorno

El entorno desarrollado cumple con las siguientes tareas:

### Gestión de Zonas

- **Crear una zona**: Permite crear una zona en el mundo de las hormigas.
- **Eliminar una zona**: Permite eliminar una zona en el mundo de las hormigas.
- **Listar las zonas**: Retorna una lista de todas las zonas existentes en el mundo de las hormigas.
- **Obtener zona por ID**: Permite obtener los detalles de una zona específica por su identificador.

### Gestión de Alimentos/Recursos

- **Crear alimentos/recursos**: Permite crear un alimento con ciertos atributos en el entorno.
- **Listar alimentos/recursos**: Permite listar los alimentos que están activos (filtrar por estado y zona).
- **Listar alimento/recurso por ID**: Permite listar los alimentos que están activos (filtrar por ID).
- **Actualizar alimentos/recursos**: Permite actualizar el estado del alimento: en proceso de recolección o recolectado (para disminuir la cantidad disponible).
- **Eliminar alimentos/recursos**: Permite eliminar el recurso y se rebaja del inventario.

### Gestión de Amenazas

- **Crear amenazas**: Permite crear una amenaza con ciertos atributos en el entorno.
- **Listar amenazas**: Permite listar amenazas activas (filtrar por estado y zona).
- **Listar amenaza por ID**: Permite listar amenazas activas (filtrar por ID).
- **Actualizar amenazas**: Permite actualizar el estado de la amenaza: sin atacar y en estado de ataque.
- **Eliminar amenazas**: Permite eliminar amenazas y se rebajan del entorno.

