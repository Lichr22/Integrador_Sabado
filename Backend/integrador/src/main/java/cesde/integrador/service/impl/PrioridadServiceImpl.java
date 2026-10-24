package cesde.integrador.service.impl;

import cesde.integrador.dto.PrioridadDto;
import cesde.integrador.entity.Prioridad;
import cesde.integrador.mapper.PrioridadMapper;
import cesde.integrador.repository.PrioridadRepository;
import cesde.integrador.service.PrioridadService;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
@Transactional
public class PrioridadServiceImpl implements PrioridadService {

    private final PrioridadRepository prioridadRepository;
    private final PrioridadMapper prioridadMapper;

    public PrioridadServiceImpl(PrioridadRepository prioridadRepository, PrioridadMapper prioridadMapper) {
        this.prioridadRepository = prioridadRepository;
        this.prioridadMapper = prioridadMapper;
    }

    @Override
    @Transactional(readOnly = true)
    public List<PrioridadDto> getAll() {
        return prioridadMapper.toDtoList(prioridadRepository.findAll());
    }

    @Override
    @Transactional(readOnly = true)
    public PrioridadDto getById(UUID id) {
        return prioridadRepository.findById(id)
                .map(prioridadMapper::toDto)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Prioridad no encontrada"));
    }

    @Override
    public PrioridadDto create(PrioridadDto dto) {
        if (dto == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Los datos de la prioridad son requeridos");
        }
        if (dto.getNombre() == null || dto.getNombre().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "El nombre de la prioridad es obligatorio");
        }
        if (dto.getId() == null) {
            dto.setId(UUID.randomUUID());
        }

        Prioridad entity = prioridadMapper.toEntity(dto);
        Prioridad saved = prioridadRepository.save(entity);
        return prioridadMapper.toDto(saved);
    }

    @Override
    public PrioridadDto update(UUID id, PrioridadDto dto) {
        if (dto == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Los datos de actualización son requeridos");
        }
        Prioridad existing = prioridadRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Prioridad no encontrada"));

        if (dto.getNombre() != null && !dto.getNombre().isBlank()) {
            existing.setNombre(dto.getNombre());
        }
        if (dto.getNivel() != null) {
            existing.setNivel(dto.getNivel());
        }
        if (dto.getDiasMaxRespuesta() != null) {
            existing.setDiasMaxRespuesta(dto.getDiasMaxRespuesta());
        }

        Prioridad updated = prioridadRepository.save(existing);
        return prioridadMapper.toDto(updated);
    }

    @Override
    public void delete(UUID id) {
        if (!prioridadRepository.existsById(id)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Prioridad no encontrada");
        }
        prioridadRepository.deleteById(id);
    }
}
