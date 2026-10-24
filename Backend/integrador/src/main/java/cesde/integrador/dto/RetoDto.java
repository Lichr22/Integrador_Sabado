package cesde.integrador.dto;

import java.time.LocalDate;
import java.util.UUID;

public class RetoDto {

    private UUID id;
    private String nombre;
    private String descripcion;
    private LocalDate fechaInicio;
    private LocalDate fechaFin;
    private String estado;
    private UUID empresaId;
    private String empresaNombre;
    private UUID categoriaId;
    private String categoriaNombre;
    private UUID prioridadId;
    private String prioridadNombre;

    public RetoDto() {
    }

    public RetoDto(UUID id, String nombre, String descripcion, LocalDate fechaInicio, LocalDate fechaFin, String estado, UUID empresaId, String empresaNombre, UUID categoriaId, String categoriaNombre, UUID prioridadId, String prioridadNombre) {
        this.id = id;
        this.nombre = nombre;
        this.descripcion = descripcion;
        this.fechaInicio = fechaInicio;
        this.fechaFin = fechaFin;
        this.estado = estado;
        this.empresaId = empresaId;
        this.empresaNombre = empresaNombre;
        this.categoriaId = categoriaId;
        this.categoriaNombre = categoriaNombre;
        this.prioridadId = prioridadId;
        this.prioridadNombre = prioridadNombre;
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

    public LocalDate getFechaInicio() {
        return fechaInicio;
    }

    public void setFechaInicio(LocalDate fechaInicio) {
        this.fechaInicio = fechaInicio;
    }

    public LocalDate getFechaFin() {
        return fechaFin;
    }

    public void setFechaFin(LocalDate fechaFin) {
        this.fechaFin = fechaFin;
    }

    public String getEstado() {
        return estado;
    }

    public void setEstado(String estado) {
        this.estado = estado;
    }

    public UUID getEmpresaId() {
        return empresaId;
    }

    public void setEmpresaId(UUID empresaId) {
        this.empresaId = empresaId;
    }

    public String getEmpresaNombre() {
        return empresaNombre;
    }

    public void setEmpresaNombre(String empresaNombre) {
        this.empresaNombre = empresaNombre;
    }

    public UUID getCategoriaId() {
        return categoriaId;
    }

    public void setCategoriaId(UUID categoriaId) {
        this.categoriaId = categoriaId;
    }

    public String getCategoriaNombre() {
        return categoriaNombre;
    }

    public void setCategoriaNombre(String categoriaNombre) {
        this.categoriaNombre = categoriaNombre;
    }

    public UUID getPrioridadId() {
        return prioridadId;
    }

    public void setPrioridadId(UUID prioridadId) {
        this.prioridadId = prioridadId;
    }

    public String getPrioridadNombre() {
        return prioridadNombre;
    }

    public void setPrioridadNombre(String prioridadNombre) {
        this.prioridadNombre = prioridadNombre;
    }
}
