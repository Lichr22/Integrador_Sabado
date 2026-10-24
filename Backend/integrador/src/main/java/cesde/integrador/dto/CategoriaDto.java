package cesde.integrador.dto;

import java.util.UUID;

public class CategoriaDto {

    private UUID id;
    private String nombre;
    private String descripcion;
    private String areaResponsable;

    public CategoriaDto() {
    }

    public CategoriaDto(UUID id, String nombre, String descripcion, String areaResponsable) {
        this.id = id;
        this.nombre = nombre;
        this.descripcion = descripcion;
        this.areaResponsable = areaResponsable;
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

    public String getDescripcion() {
        return descripcion;
    }

    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
    }

    public String getAreaResponsable() {
        return areaResponsable;
    }

    public void setAreaResponsable(String areaResponsable) {
        this.areaResponsable = areaResponsable;
    }
}
