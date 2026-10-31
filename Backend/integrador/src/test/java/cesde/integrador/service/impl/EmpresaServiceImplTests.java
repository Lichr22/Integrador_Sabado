package cesde.integrador.service.impl;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cesde.integrador.dto.EmpresaDto;
import cesde.integrador.entity.Empresa;
import cesde.integrador.mapper.EmpresaMapper;
import cesde.integrador.repository.EmpresaRepository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mapstruct.factory.Mappers;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

@ExtendWith(MockitoExtension.class)
@DisplayName("EmpresaServiceImpl: reglas de negocio de empresas")
class EmpresaServiceImplTests {
    @Mock
    private EmpresaRepository repository;
    private final EmpresaMapper mapper = Mappers.getMapper(EmpresaMapper.class);
    private EmpresaServiceImpl service;

    @BeforeEach
    void setUp() {
        service = new EmpresaServiceImpl(repository, mapper);
    }

    @Test
    @DisplayName("Lista todas las empresas convertidas a DTO")
    void getAllReturnsMappedCompanies() {
        when(repository.findAll()).thenReturn(List.of(empresa("Acme"), empresa("Globex")));

        List<EmpresaDto> result = service.getAll();

        assertEquals(2, result.size());
        assertEquals("Acme", result.get(0).getNombre());
    }

    @Test
    @DisplayName("Consultar una empresa inexistente responde 404")
    void getByIdMissingIsNotFound() {
        UUID id = UUID.randomUUID();
        when(repository.findById(id)).thenReturn(Optional.empty());

        ResponseStatusException error = assertThrows(ResponseStatusException.class, () -> service.getById(id));

        assertEquals(HttpStatus.NOT_FOUND, error.getStatusCode());
    }

    @Test
    @DisplayName("Crear sin datos responde 400")
    void createWithoutDataIsBadRequest() {
        ResponseStatusException error = assertThrows(ResponseStatusException.class, () -> service.create(null));

        assertEquals(HttpStatus.BAD_REQUEST, error.getStatusCode());
        verify(repository, never()).save(any());
    }

    @Test
    @DisplayName("Crear sin nombre responde 400 y no guarda")
    void createWithBlankNameIsBadRequest() {
        EmpresaDto dto = new EmpresaDto();
        dto.setNombre("   ");

        ResponseStatusException error = assertThrows(ResponseStatusException.class, () -> service.create(dto));

        assertEquals("El nombre de la empresa es obligatorio", error.getReason());
        verify(repository, never()).save(any());
    }

    @Test
    @DisplayName("Crear asigna un ID y la marca activa por defecto")
    void createAssignsIdAndActiveByDefault() {
        EmpresaDto dto = new EmpresaDto();
        dto.setNombre("Nueva empresa");
        when(repository.save(any(Empresa.class))).thenAnswer(invocation -> invocation.getArgument(0));

        EmpresaDto result = service.create(dto);

        assertNotNull(result.getId());
        assertTrue(result.getActiva());
        assertEquals("Nueva empresa", result.getNombre());
    }

    @Test
    @DisplayName("Actualizar solo cambia los campos enviados")
    void updateChangesOnlyProvidedFields() {
        Empresa existing = empresa("Acme");
        existing.setSector("Tecnología");
        when(repository.findById(existing.getId())).thenReturn(Optional.of(existing));
        when(repository.save(any(Empresa.class))).thenAnswer(invocation -> invocation.getArgument(0));
        EmpresaDto changes = new EmpresaDto();
        changes.setNombre("");
        changes.setTelefono("3001234567");
        changes.setActiva(false);

        service.update(existing.getId(), changes);

        ArgumentCaptor<Empresa> saved = ArgumentCaptor.forClass(Empresa.class);
        verify(repository).save(saved.capture());
        assertEquals("Acme", saved.getValue().getNombre());
        assertEquals("Tecnología", saved.getValue().getSector());
        assertEquals("3001234567", saved.getValue().getTelefono());
        assertEquals(false, saved.getValue().getActiva());
    }

    @Test
    @DisplayName("Actualizar una empresa inexistente responde 404")
    void updateMissingIsNotFound() {
        UUID id = UUID.randomUUID();
        when(repository.findById(id)).thenReturn(Optional.empty());

        ResponseStatusException error =
                assertThrows(ResponseStatusException.class, () -> service.update(id, new EmpresaDto()));

        assertEquals(HttpStatus.NOT_FOUND, error.getStatusCode());
    }

    @Test
    @DisplayName("Eliminar una empresa existente la borra del repositorio")
    void deleteExistingRemovesIt() {
        UUID id = UUID.randomUUID();
        when(repository.existsById(id)).thenReturn(true);

        service.delete(id);

        verify(repository).deleteById(id);
    }

    @Test
    @DisplayName("Eliminar una empresa inexistente responde 404 y no borra nada")
    void deleteMissingIsNotFound() {
        UUID id = UUID.randomUUID();
        when(repository.existsById(id)).thenReturn(false);

        assertThrows(ResponseStatusException.class, () -> service.delete(id));
        verify(repository, never()).deleteById(any());
    }

    private static Empresa empresa(String nombre) {
        return new Empresa(UUID.randomUUID(), nombre, "900123456", null, null, null, null, true);
    }
}
