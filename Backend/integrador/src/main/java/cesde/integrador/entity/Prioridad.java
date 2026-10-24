package cesde.integrador.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.util.UUID;

@Entity
@Table(name = "prioridades", schema = "public")
public class Prioridad {

    @Id
    @Column(name = "id", nullable = false)
    private UUID id;

    @Column(name = "nombre")
    private String nombre;

    @Column(name = "nivel")
    private Short nivel;

    @Column(name = "dias_max_respuesta")
    private Short diasMaxRespuesta;

    public Prioridad() {
    }

    public Prioridad(UUID id, String nombre, Short nivel, Short diasMaxRespuesta) {
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
