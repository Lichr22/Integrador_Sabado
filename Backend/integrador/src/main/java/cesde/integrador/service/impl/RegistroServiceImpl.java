package cesde.integrador.service.impl;

import cesde.integrador.dto.RegistroDto;
import cesde.integrador.entity.Registro;
import cesde.integrador.entity.Reto;
import cesde.integrador.entity.Usuario;
import cesde.integrador.mapper.RegistroMapper;
import cesde.integrador.repository.RegistroRepository;
import cesde.integrador.repository.RetoRepository;
import cesde.integrador.repository.UsuarioRepository;
import cesde.integrador.service.RegistroService;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
@Transactional
public class RegistroServiceImpl implements RegistroService {

    private final RegistroRepository registroRepository;
    private final UsuarioRepository usuarioRepository;
    private final RetoRepository retoRepository;
    private final RegistroMapper registroMapper;

    public RegistroServiceImpl(
            RegistroRepository registroRepository,
            UsuarioRepository usuarioRepository,
            RetoRepository retoRepository,
            RegistroMapper registroMapper) {
        this.registroRepository = registroRepository;
        this.usuarioRepository = usuarioRepository;
        this.retoRepository = retoRepository;
        this.registroMapper = registroMapper;
    }

    @Override
    @Transactional(readOnly = true)
    public List<RegistroDto> getAll() {
        return registroMapper.toDtoList(registroRepository.findAll());
    }

    @Override
    @Transactional(readOnly = true)
    public RegistroDto getById(UUID id) {
        return registroRepository.findById(id)
                .map(registroMapper::toDto)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Registro de inscripción no encontrado"));
    }

    @Override
    public RegistroDto create(RegistroDto dto) {
        if (dto == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Los datos de la inscripción son requeridos");
        }
        if (dto.getUsuarioId() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "El usuario participante es obligatorio");
        }
        if (dto.getRetoId() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "El reto es obligatorio");
        }

        Usuario usuario = usuarioRepository.findById(dto.getUsuarioId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.BAD_REQUEST, "El usuario seleccionado no existe"));

        Reto reto = retoRepository.findById(dto.getRetoId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.BAD_REQUEST, "El reto seleccionado no existe"));

        if (dto.getId() == null) {
            dto.setId(UUID.randomUUID());
        }
        if (dto.getEstado() == null || dto.getEstado().isBlank()) {
            dto.setEstado("Inscrito");
        }
        if (dto.getFechaRegistro() == null) {
            dto.setFechaRegistro(LocalDateTime.now());
        }

        Registro entity = registroMapper.toEntity(dto);
        entity.setUsuario(usuario);
        entity.setReto(reto);

        Registro saved = registroRepository.save(entity);
        return registroMapper.toDto(saved);
    }

    @Override
    public RegistroDto update(UUID id, RegistroDto dto) {
        if (dto == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Los datos de actualización son requeridos");
        }
        Registro existing = registroRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Registro de inscripción no encontrado"));

        if (dto.getObservacion() != null) {
            existing.setObservacion(dto.getObservacion());
        }
        if (dto.getEstado() != null && !dto.getEstado().isBlank()) {
            existing.setEstado(dto.getEstado());
        }
        if (dto.getFechaRegistro() != null) {
            existing.setFechaRegistro(dto.getFechaRegistro());
        }

        if (dto.getUsuarioId() != null) {
            Usuario usuario = usuarioRepository.findById(dto.getUsuarioId())
                    .orElseThrow(() -> new ResponseStatusException(HttpStatus.BAD_REQUEST, "El usuario seleccionado no existe"));
            existing.setUsuario(usuario);
        }
        if (dto.getRetoId() != null) {
            Reto reto = retoRepository.findById(dto.getRetoId())
                    .orElseThrow(() -> new ResponseStatusException(HttpStatus.BAD_REQUEST, "El reto seleccionado no existe"));
            existing.setReto(reto);
        }

        Registro updated = registroRepository.save(existing);
        return registroMapper.toDto(updated);
    }

    @Override
    public void delete(UUID id) {
        if (!registroRepository.existsById(id)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Registro de inscripción no encontrado");
        }
        registroRepository.deleteById(id);
    }
}
