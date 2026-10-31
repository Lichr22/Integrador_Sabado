package cesde.integrador.service.impl;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cesde.integrador.dto.RetoDto;
import cesde.integrador.entity.Categoria;
import cesde.integrador.entity.Empresa;
import cesde.integrador.entity.Prioridad;
import cesde.integrador.entity.Reto;
import cesde.integrador.mapper.RetoMapper;
import cesde.integrador.repository.CategoriaRepository;
import cesde.integrador.repository.EmpresaRepository;
import cesde.integrador.repository.PrioridadRepository;
import cesde.integrador.repository.RetoRepository;
import java.time.LocalDate;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.mapstruct.factory.Mappers;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

@ExtendWith(MockitoExtension.class)
@DisplayName("RetoServiceImpl: reglas de negocio de retos")
class RetoServiceImplTests {
    @Mock
    private RetoRepository retos;
    @Mock
    private EmpresaRepository empresas;
    @Mock
    private CategoriaRepository categorias;
    @Mock
    private PrioridadRepository prioridades;
    private final RetoMapper mapper = Mappers.getMapper(RetoMapper.class);
    private RetoServiceImpl service;

    private final Empresa empresa = new Empresa(UUID.randomUUID(), "Acme", null, null, null, null, null, true);
    private final Categoria categoria = new Categoria();
    private final Prioridad prioridad = new Prioridad();

    @BeforeEach
    void setUp() {
        service = new RetoServiceImpl(retos, empresas, categorias, prioridades, mapper);
        categoria.setId(UUID.randomUUID());
        categoria.setNombre("Logística");
        prioridad.setId(UUID.randomUUID());
        prioridad.setNombre("Alta");
    }

    static Stream<Arguments> missingRequiredFields() {
        return Stream.of(
                Arguments.of("nombre", (Consumer<RetoDto>) dto -> dto.setNombre(" "),
                        "El nombre del reto es obligatorio"),
                Arguments.of("empresa", (Consumer<RetoDto>) dto -> dto.setEmpresaId(null),
                        "La empresa vinculada es obligatoria"),
                Arguments.of("categoría", (Consumer<RetoDto>) dto -> dto.setCategoriaId(null),
                        "La categoría vinculada es obligatoria"),
                Arguments.of("prioridad", (Consumer<RetoDto>) dto -> dto.setPrioridadId(null),
                        "La prioridad vinculada es obligatoria"));
    }

    @ParameterizedTest(name = "Sin {0}: \"{2}\"")
    @DisplayName("Crear sin un campo obligatorio responde 400")
    @MethodSource("missingRequiredFields")
    void createWithoutRequiredFieldIsBadRequest(String field, Consumer<RetoDto> change, String message) {
        RetoDto dto = validDto();
        change.accept(dto);

        ResponseStatusException error = assertThrows(ResponseStatusException.class, () -> service.create(dto));

        assertEquals(HttpStatus.BAD_REQUEST, error.getStatusCode());
        assertEquals(message, error.getReason());
        verify(retos, never()).save(any());
    }

    @Test
    @DisplayName("Crear con una empresa que no existe responde 400")
    void createWithUnknownCompanyIsBadRequest() {
        RetoDto dto = validDto();
        when(empresas.findById(dto.getEmpresaId())).thenReturn(Optional.empty());

        ResponseStatusException error = assertThrows(ResponseStatusException.class, () -> service.create(dto));

        assertEquals("La empresa seleccionada no existe", error.getReason());
        verify(retos, never()).save(any());
    }

    @Test
    @DisplayName("Crear vincula las relaciones, asigna ID y estado \"Activo\" por defecto")
    void createLinksRelationsAndDefaults() {
        RetoDto dto = validDto();
        givenRelationsExist();
        when(retos.save(any(Reto.class))).thenAnswer(invocation -> invocation.getArgument(0));

        RetoDto result = service.create(dto);

        assertNotNull(result.getId());
        assertEquals("Activo", result.getEstado());
        assertEquals("Acme", result.getEmpresaNombre());
        assertEquals("Logística", result.getCategoriaNombre());
        assertEquals("Alta", result.getPrioridadNombre());
    }

    @Test
    @DisplayName("Crear conserva el estado enviado")
    void createKeepsProvidedState() {
        RetoDto dto = validDto();
        dto.setEstado("Cerrado");
        givenRelationsExist();
        when(retos.save(any(Reto.class))).thenAnswer(invocation -> invocation.getArgument(0));

        assertEquals("Cerrado", service.create(dto).getEstado());
    }

    @Test
    @DisplayName("Actualizar con una prioridad inexistente responde 400")
    void updateWithUnknownPriorityIsBadRequest() {
        Reto existing = new Reto(UUID.randomUUID(), "Reto", null, null, null, "Abierto", empresa, categoria, prioridad);
        when(retos.findById(existing.getId())).thenReturn(Optional.of(existing));
        RetoDto changes = new RetoDto();
        changes.setPrioridadId(UUID.randomUUID());
        when(prioridades.findById(changes.getPrioridadId())).thenReturn(Optional.empty());

        ResponseStatusException error =
                assertThrows(ResponseStatusException.class, () -> service.update(existing.getId(), changes));

        assertEquals("La prioridad seleccionada no existe", error.getReason());
        verify(retos, never()).save(any());
    }

    @Test
    @DisplayName("Actualizar cambia las fechas y conserva el nombre si llega vacío")
    void updateChangesDatesAndKeepsName() {
        Reto existing = new Reto(UUID.randomUUID(), "Reto original", null, null, null, "Abierto", empresa, categoria, prioridad);
        when(retos.findById(existing.getId())).thenReturn(Optional.of(existing));
        when(retos.save(any(Reto.class))).thenAnswer(invocation -> invocation.getArgument(0));
        RetoDto changes = new RetoDto();
        changes.setNombre("");
        changes.setFechaFin(LocalDate.of(2026, 12, 31));

        RetoDto result = service.update(existing.getId(), changes);

        assertEquals("Reto original", result.getNombre());
        assertEquals(LocalDate.of(2026, 12, 31), result.getFechaFin());
        assertEquals("Abierto", result.getEstado());
    }

    private void givenRelationsExist() {
        when(empresas.findById(empresa.getId())).thenReturn(Optional.of(empresa));
        when(categorias.findById(categoria.getId())).thenReturn(Optional.of(categoria));
        when(prioridades.findById(prioridad.getId())).thenReturn(Optional.of(prioridad));
    }

    private RetoDto validDto() {
        RetoDto dto = new RetoDto();
        dto.setNombre("Reducir tiempos de entrega");
        dto.setEmpresaId(empresa.getId());
        dto.setCategoriaId(categoria.getId());
        dto.setPrioridadId(prioridad.getId());
        return dto;
    }
}
