package cesde.integrador.dto;

import java.time.LocalDateTime;
import java.util.UUID;

public class UsuarioDto {

    private UUID id;
    private String nombre;
    private String correo;
    private Boolean activo;
    private String rol;
    private LocalDateTime fechaRegistro;
    private String contrasena;

    public UsuarioDto() {
    }

    public UsuarioDto(UUID id, String nombre, String correo, Boolean activo, String rol, LocalDateTime fechaRegistro) {
        this(id, nombre, correo, activo, rol, fechaRegistro, null);
    }

    public UsuarioDto(UUID id, String nombre, String correo, Boolean activo, String rol, LocalDateTime fechaRegistro, String contrasena) {
        this.id = id;
        this.nombre = nombre;
        this.correo = correo;
        this.activo = activo;
        this.rol = rol;
        this.fechaRegistro = fechaRegistro;
        this.contrasena = contrasena;
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

    public String getCorreo() {
        return correo;
    }

    public void setCorreo(String correo) {
        this.correo = correo;
    }

    public Boolean getActivo() {
        return activo;
    }

    public void setActivo(Boolean activo) {
        this.activo = activo;
    }

    public String getRol() {
        return rol;
    }

    public void setRol(String rol) {
        this.rol = rol;
    }

    public LocalDateTime getFechaRegistro() {
        return fechaRegistro;
    }

    public void setFechaRegistro(LocalDateTime fechaRegistro) {
        this.fechaRegistro = fechaRegistro;
    }

    public String getContrasena() {
        return contrasena;
    }

    public void setContrasena(String contrasena) {
        this.contrasena = contrasena;
    }
}
