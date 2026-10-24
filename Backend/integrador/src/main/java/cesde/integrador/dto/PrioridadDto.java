package cesde.integrador.dto;

import java.util.UUID;

public class PrioridadDto {

    private UUID id;
    private String nombre;
    private Short nivel;
    private Short diasMaxRespuesta;

    public PrioridadDto() {
    }

    public PrioridadDto(UUID id, String nombre, Short nivel, Short diasMaxRespuesta) {
        this.id = id;
        this.nombre = nombre;
        this.nivel = nivel;
        this.diasMaxRespuesta = diasMaxRespuesta;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getNombre() {
        return nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public Short getNivel() {
        return nivel;
    }

    public void setNivel(Short nivel) {
        this.nivel = nivel;
    }

    public Short getDiasMaxRespuesta() {
        return diasMaxRespuesta;
    }

    public void setDiasMaxRespuesta(Short diasMaxRespuesta) {
        this.diasMaxRespuesta = diasMaxRespuesta;
    }
}
