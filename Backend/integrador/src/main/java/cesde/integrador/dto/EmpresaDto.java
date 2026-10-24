package cesde.integrador.dto;

import java.util.UUID;

public class EmpresaDto {

    private UUID id;
    private String nombre;
    private String nit;
    private String sector;
    private String contacto;
    private String correo;
    private String telefono;
    private Boolean activa;

    public EmpresaDto() {
    }

    public EmpresaDto(UUID id, String nombre, String nit, String sector, String contacto, String correo, String telefono, Boolean activa) {
        this.id = id;
        this.nombre = nombre;
        this.nit = nit;
        this.sector = sector;
        this.contacto = contacto;
        this.correo = correo;
        this.telefono = telefono;
        this.activa = activa;
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

    public String getNit() {
        return nit;
    }

    public void setNit(String nit) {
        this.nit = nit;
    }

    public String getSector() {
        return sector;
    }

    public void setSector(String sector) {
        this.sector = sector;
    }

    public String getContacto() {
        return contacto;
    }

    public void setContacto(String contacto) {
        this.contacto = contacto;
    }

    public String getCorreo() {
        return correo;
    }

    public void setCorreo(String correo) {
        this.correo = correo;
    }

    public String getTelefono() {
        return telefono;
    }

    public void setTelefono(String telefono) {
        this.telefono = telefono;
    }

    public Boolean getActiva() {
        return activa;
    }

    public void setActiva(Boolean activa) {
        this.activa = activa;
    }
}
