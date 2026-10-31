# Evaluación Técnica: three.ws 3D Agent Studio (`nirholas/three.ws`)

## 1. Resumen Ejecutivo
- **Repositorio:** [github.com/nirholas/three.ws](https://github.com/nirholas/three.ws)
- **Licencia:** Apache-2.0
- **Propósito:** Plataforma integral para agentes 3D, avatares WebGL/Three.js, generación de modelos 3D (GLB), rigging automático, animación y pago por microtransacciones (x402).
- **Estado de Evaluación:** Aprobado e integrado en `mcp/catalog.json`.

---

## 2. Arquitectura y Capacidades
`three.ws` es un ecosistema multi-capa enfocado en dar cuerpos 3D a agentes de IA (Claude, GPT, Gemini) en navegadores y entornos interactivos:
1. **Avatar SDK & Character Studio (`character-studio/`, `avatar-sdk/`):**
   - Soporte nativo para avatares glTF / GLB con blendshapes faciales (morph targets), lip-sync de voz y compatibilidad con VRM / Ready Player Me.
   - Componentes web nativos (`<three-agent>`, `<three-avatar>`) para incrustar avatares 3D interactivos en cualquier web o dashboard.
2. **Servidor MCP 3D Studio (`server-3d.json`):**
   - Expone endpoints MCP para generar assets 3D desde texto o imágenes, agregar rigging automático, aplicar retargeting de animaciones y exportar archivos GLB optimizados con compresión Draco.
   - Endpoint remoto streamable-http: `https://three.ws/api/mcp-3d`.
3. **Agentes Autónomos y Pagos x402:**
   - Permite a los agentes interactuar en mundos 3D y ejecutar microtransacciones autónomas basadas en protocolos de pago para agentes de IA.

---

## 3. Configuración para Antigravity / Claude Desktop
### Opción A: Conexión Remota (Streamable HTTP)
```json
{
  "mcpServers": {
    "threews-3d": {
      "url": "https://three.ws/api/mcp-3d"
    }
  }
}
```

### Opción B: Ejecución Local (Node / NPM)
```json
{
  "mcpServers": {
    "threews-studio-local": {
      "command": "node",
      "args": ["mcp/evaluated/three.ws/api/3d/server.js"],
      "env": {}
    }
  }
}
```

---

## 4. Aplicabilidad al Proyecto Actual
- Facilita la previsualización e interacción web de los modelos exportados (`kobold_godot_ready.glb`) directamente en el navegador sin abrir Blender ni Godot.
- Provee un puente rápido para rigging y blendshapes si se desean añadir expresiones faciales o lip-sync a los personajes portados.
