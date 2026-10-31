package cesde.integrador.mapper;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import cesde.integrador.dto.RetoDto;
import cesde.integrador.entity.Categoria;
import cesde.integrador.entity.Empresa;
import cesde.integrador.entity.Prioridad;
import cesde.integrador.entity.Reto;
import java.time.LocalDate;
import java.util.UUID;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mapstruct.factory.Mappers;

@DisplayName("RetoMapper: conversión entre entidad y DTO")
class RetoMapperTests {
    private final RetoMapper mapper = Mappers.getMapper(RetoMapper.class);

    @Test
    @DisplayName("Copia los IDs y nombres de empresa, categoría y prioridad al DTO")
    void toDtoFlattensRelations() {
        Empresa empresa = new Empresa(UUID.randomUUID(), "Acme", null, null, null, null, null, true);
        Categoria categoria = new Categoria();
        categoria.setId(UUID.randomUUID());
        categoria.setNombre("Logística");
        Prioridad prioridad = new Prioridad();
        prioridad.setId(UUID.randomUUID());
        prioridad.setNombre("Alta");
        Reto reto = new Reto(UUID.randomUUID(), "Reto", "Descripción",
                LocalDate.of(2026, 1, 1), LocalDate.of(2026, 6, 30), "Abierto", empresa, categoria, prioridad);

        RetoDto dto = mapper.toDto(reto);

        assertEquals(reto.getId(), dto.getId());
        assertEquals(LocalDate.of(2026, 6, 30), dto.getFechaFin());
        assertEquals(empresa.getId(), dto.getEmpresaId());
        assertEquals("Acme", dto.getEmpresaNombre());
        assertEquals(categoria.getId(), dto.getCategoriaId());
        assertEquals("Logística", dto.getCategoriaNombre());
        assertEquals(prioridad.getId(), dto.getPrioridadId());
        assertEquals("Alta", dto.getPrioridadNombre());
    }

    @Test
    @DisplayName("Un reto sin relaciones produce IDs nulos sin fallar")
    void toDtoWithoutRelations() {
        RetoDto dto = mapper.toDto(new Reto());

        assertNull(dto.getEmpresaId());
        assertNull(dto.getCategoriaNombre());
    }

    @Test
    @DisplayName("Al convertir a entidad no crea relaciones: las asigna el servicio")
    void toEntityIgnoresRelations() {
        RetoDto dto = new RetoDto();
        dto.setNombre("Reto");
        dto.setEmpresaId(UUID.randomUUID());

        Reto entity = mapper.toEntity(dto);

        assertEquals("Reto", entity.getNombre());
        assertNull(entity.getEmpresa());
    }
}
