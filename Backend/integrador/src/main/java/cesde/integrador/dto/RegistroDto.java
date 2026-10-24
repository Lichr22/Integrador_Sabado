package cesde.integrador.dto;

import java.time.LocalDateTime;
import java.util.UUID;

public class RegistroDto {

    private UUID id;
    private LocalDateTime fechaRegistro;
    private String observacion;
    private String estado;
    private UUID usuarioId;
    private String usuarioNombre;
    private UUID retoId;
    private String retoNombre;

    public RegistroDto() {
    }

    public RegistroDto(UUID id, LocalDateTime fechaRegistro, String observacion, String estado, UUID usuarioId, String usuarioNombre, UUID retoId, String retoNombre) {
        this.id = id;
        this.fechaRegistro = fechaRegistro;
        this.observacion = observacion;
        this.estado = estado;
        this.usuarioId = usuarioId;
        this.usuarioNombre = usuarioNombre;
        this.retoId = retoId;
        this.retoNombre = retoNombre;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public LocalDateTime getFechaRegistro() {
        return fechaRegistro;
    }

    public void setFechaRegistro(LocalDateTime fechaRegistro) {
        this.fechaRegistro = fechaRegistro;
    }

    public String getObservacion() {
        return observacion;
    }

    public void setObservacion(String observacion) {
        this.observacion = observacion;
    }

    public String getEstado() {
        return estado;
    }

    public void setEstado(String estado) {
        this.estado = estado;
    }

    public UUID getUsuarioId() {
        return usuarioId;
    }

    public void setUsuarioId(UUID usuarioId) {
        this.usuarioId = usuarioId;
    }

    public String getUsuarioNombre() {
        return usuarioNombre;
    }

    public void setUsuarioNombre(String usuarioNombre) {
        this.usuarioNombre = usuarioNombre;
    }

    public UUID getRetoId() {
        return retoId;
    }

    public void setRetoId(UUID retoId) {
        this.retoId = retoId;
    }

    public String getRetoNombre() {
        return retoNombre;
    }

    public void setRetoNombre(String retoNombre) {
        this.retoNombre = retoNombre;
    }
}
