package cesde.integrador.service.impl;

import cesde.integrador.dto.EmpresaDto;
import cesde.integrador.entity.Empresa;
import cesde.integrador.mapper.EmpresaMapper;
import cesde.integrador.repository.EmpresaRepository;
import cesde.integrador.service.EmpresaService;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
@Transactional
public class EmpresaServiceImpl implements EmpresaService {

    private final EmpresaRepository empresaRepository;
    private final EmpresaMapper empresaMapper;

    public EmpresaServiceImpl(EmpresaRepository empresaRepository, EmpresaMapper empresaMapper) {
        this.empresaRepository = empresaRepository;
        this.empresaMapper = empresaMapper;
    }

    @Override
    @Transactional(readOnly = true)
    public List<EmpresaDto> getAll() {
        return empresaMapper.toDtoList(empresaRepository.findAll());
    }

    @Override
    @Transactional(readOnly = true)
    public EmpresaDto getById(UUID id) {
        return empresaRepository.findById(id)
                .map(empresaMapper::toDto)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Empresa no encontrada"));
    }

    @Override
    public EmpresaDto create(EmpresaDto dto) {
        if (dto == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Los datos de la empresa son requeridos");
        }
        if (dto.getNombre() == null || dto.getNombre().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "El nombre de la empresa es obligatorio");
        }
        if (dto.getId() == null) {
            dto.setId(UUID.randomUUID());
        }
        if (dto.getActiva() == null) {
            dto.setActiva(true);
        }

        Empresa entity = empresaMapper.toEntity(dto);
        Empresa saved = empresaRepository.save(entity);
        return empresaMapper.toDto(saved);
    }

    @Override
    public EmpresaDto update(UUID id, EmpresaDto dto) {
        if (dto == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Los datos de actualización son requeridos");
        }
        Empresa existing = empresaRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Empresa no encontrada"));

        if (dto.getNombre() != null && !dto.getNombre().isBlank()) {
            existing.setNombre(dto.getNombre());
        }
        if (dto.getNit() != null) {
            existing.setNit(dto.getNit());
        }
        if (dto.getSector() != null) {
            existing.setSector(dto.getSector());
        }
        if (dto.getContacto() != null) {
            existing.setContacto(dto.getContacto());
        }
        if (dto.getCorreo() != null) {
            existing.setCorreo(dto.getCorreo());
        }
        if (dto.getTelefono() != null) {
            existing.setTelefono(dto.getTelefono());
        }
        if (dto.getActiva() != null) {
            existing.setActiva(dto.getActiva());
        }

        Empresa updated = empresaRepository.save(existing);
        return empresaMapper.toDto(updated);
    }

    @Override
    public void delete(UUID id) {
        if (!empresaRepository.existsById(id)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Empresa no encontrada");
        }
        empresaRepository.deleteById(id);
    }
}
