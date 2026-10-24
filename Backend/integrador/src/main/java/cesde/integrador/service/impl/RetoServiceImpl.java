package cesde.integrador.service.impl;

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
import cesde.integrador.service.RetoService;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
@Transactional
public class RetoServiceImpl implements RetoService {

    private final RetoRepository retoRepository;
    private final EmpresaRepository empresaRepository;
    private final CategoriaRepository categoriaRepository;
    private final PrioridadRepository prioridadRepository;
    private final RetoMapper retoMapper;

    public RetoServiceImpl(
            RetoRepository retoRepository,
            EmpresaRepository empresaRepository,
            CategoriaRepository categoriaRepository,
            PrioridadRepository prioridadRepository,
            RetoMapper retoMapper) {
        this.retoRepository = retoRepository;
        this.empresaRepository = empresaRepository;
        this.categoriaRepository = categoriaRepository;
        this.prioridadRepository = prioridadRepository;
        this.retoMapper = retoMapper;
    }

    @Override
    @Transactional(readOnly = true)
    public List<RetoDto> getAll() {
        return retoMapper.toDtoList(retoRepository.findAll());
    }

    @Override
    @Transactional(readOnly = true)
    public RetoDto getById(UUID id) {
        return retoRepository.findById(id)
                .map(retoMapper::toDto)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Reto no encontrado"));
    }

    @Override
    public RetoDto create(RetoDto dto) {
        if (dto == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Los datos del reto son requeridos");
        }
        if (dto.getNombre() == null || dto.getNombre().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "El nombre del reto es obligatorio");
        }
        if (dto.getEmpresaId() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "La empresa vinculada es obligatoria");
        }
        if (dto.getCategoriaId() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "La categoría vinculada es obligatoria");
        }
        if (dto.getPrioridadId() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "La prioridad vinculada es obligatoria");
        }

        Empresa empresa = empresaRepository.findById(dto.getEmpresaId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.BAD_REQUEST, "La empresa seleccionada no existe"));

        Categoria categoria = categoriaRepository.findById(dto.getCategoriaId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.BAD_REQUEST, "La categoría seleccionada no existe"));

        Prioridad prioridad = prioridadRepository.findById(dto.getPrioridadId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.BAD_REQUEST, "La prioridad seleccionada no existe"));

        if (dto.getId() == null) {
            dto.setId(UUID.randomUUID());
        }
        if (dto.getEstado() == null || dto.getEstado().isBlank()) {
            dto.setEstado("Activo");
        }

        Reto entity = retoMapper.toEntity(dto);
        entity.setEmpresa(empresa);
        entity.setCategoria(categoria);
        entity.setPrioridad(prioridad);

        Reto saved = retoRepository.save(entity);
        return retoMapper.toDto(saved);
    }

    @Override
    public RetoDto update(UUID id, RetoDto dto) {
        if (dto == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Los datos de actualización son requeridos");
        }
        Reto existing = retoRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Reto no encontrado"));

        if (dto.getNombre() != null && !dto.getNombre().isBlank()) {
            existing.setNombre(dto.getNombre());
        }
        if (dto.getDescripcion() != null) {
            existing.setDescripcion(dto.getDescripcion());
        }
        if (dto.getFechaInicio() != null) {
            existing.setFechaInicio(dto.getFechaInicio());
        }
        if (dto.getFechaFin() != null) {
            existing.setFechaFin(dto.getFechaFin());
        }
        if (dto.getEstado() != null && !dto.getEstado().isBlank()) {
            existing.setEstado(dto.getEstado());
        }

        if (dto.getEmpresaId() != null) {
            Empresa empresa = empresaRepository.findById(dto.getEmpresaId())
                    .orElseThrow(() -> new ResponseStatusException(HttpStatus.BAD_REQUEST, "La empresa seleccionada no existe"));
            existing.setEmpresa(empresa);
        }
        if (dto.getCategoriaId() != null) {
            Categoria categoria = categoriaRepository.findById(dto.getCategoriaId())
                    .orElseThrow(() -> new ResponseStatusException(HttpStatus.BAD_REQUEST, "La categoría seleccionada no existe"));
            existing.setCategoria(categoria);
        }
        if (dto.getPrioridadId() != null) {
            Prioridad prioridad = prioridadRepository.findById(dto.getPrioridadId())
                    .orElseThrow(() -> new ResponseStatusException(HttpStatus.BAD_REQUEST, "La prioridad seleccionada no existe"));
            existing.setPrioridad(prioridad);
        }

        Reto updated = retoRepository.save(existing);
        return retoMapper.toDto(updated);
    }

    @Override
    public void delete(UUID id) {
        if (!retoRepository.existsById(id)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Reto no encontrado");
        }
        retoRepository.deleteById(id);
    }
}
