package cesde.integrador.service.impl;

import cesde.integrador.dto.CategoriaDto;
import cesde.integrador.entity.Categoria;
import cesde.integrador.mapper.CategoriaMapper;
import cesde.integrador.repository.CategoriaRepository;
import cesde.integrador.service.CategoriaService;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
@Transactional
public class CategoriaServiceImpl implements CategoriaService {

    private final CategoriaRepository categoriaRepository;
    private final CategoriaMapper categoriaMapper;

    public CategoriaServiceImpl(CategoriaRepository categoriaRepository, CategoriaMapper categoriaMapper) {
        this.categoriaRepository = categoriaRepository;
        this.categoriaMapper = categoriaMapper;
    }

    @Override
    @Transactional(readOnly = true)
    public List<CategoriaDto> getAll() {
        return categoriaMapper.toDtoList(categoriaRepository.findAll());
    }

    @Override
    @Transactional(readOnly = true)
    public CategoriaDto getById(UUID id) {
        return categoriaRepository.findById(id)
                .map(categoriaMapper::toDto)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Categoría no encontrada"));
    }

    @Override
    public CategoriaDto create(CategoriaDto dto) {
        if (dto == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Los datos de la categoría son requeridos");
        }
        if (dto.getNombre() == null || dto.getNombre().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "El nombre de la categoría es obligatorio");
        }
        if (dto.getId() == null) {
            dto.setId(UUID.randomUUID());
        }

        Categoria entity = categoriaMapper.toEntity(dto);
        Categoria saved = categoriaRepository.save(entity);
        return categoriaMapper.toDto(saved);
    }

    @Override
    public CategoriaDto update(UUID id, CategoriaDto dto) {
        if (dto == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Los datos de actualización son requeridos");
        }
        Categoria existing = categoriaRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Categoría no encontrada"));

        if (dto.getNombre() != null && !dto.getNombre().isBlank()) {
            existing.setNombre(dto.getNombre());
        }
        if (dto.getDescripcion() != null) {
            existing.setDescripcion(dto.getDescripcion());
        }
        if (dto.getAreaResponsable() != null) {
            existing.setAreaResponsable(dto.getAreaResponsable());
        }

        Categoria updated = categoriaRepository.save(existing);
        return categoriaMapper.toDto(updated);
    }

    @Override
    public void delete(UUID id) {
        if (!categoriaRepository.existsById(id)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Categoría no encontrada");
        }
        categoriaRepository.deleteById(id);
    }
}
