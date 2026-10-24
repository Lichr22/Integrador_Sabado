package cesde.integrador.service.impl;

import cesde.integrador.api.PasswordService;
import cesde.integrador.dto.UsuarioDto;
import cesde.integrador.entity.Usuario;
import cesde.integrador.mapper.UsuarioMapper;
import cesde.integrador.repository.UsuarioRepository;
import cesde.integrador.service.UsuarioService;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
@Transactional
public class UsuarioServiceImpl implements UsuarioService {

    private final UsuarioRepository usuarioRepository;
    private final UsuarioMapper usuarioMapper;
    private final PasswordService passwordService;

    public UsuarioServiceImpl(
            UsuarioRepository usuarioRepository,
            UsuarioMapper usuarioMapper,
            PasswordService passwordService) {
        this.usuarioRepository = usuarioRepository;
        this.usuarioMapper = usuarioMapper;
        this.passwordService = passwordService;
    }

    @Override
    @Transactional(readOnly = true)
    public List<UsuarioDto> getAll() {
        return usuarioMapper.toDtoList(usuarioRepository.findAll());
    }

    @Override
    @Transactional(readOnly = true)
    public UsuarioDto getById(UUID id) {
        return usuarioRepository.findById(id)
                .map(usuarioMapper::toDto)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Usuario no encontrado"));
    }

    @Override
    public UsuarioDto create(UsuarioDto dto) {
        if (dto == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Los datos del usuario son requeridos");
        }
        if (dto.getNombre() == null || dto.getNombre().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "El nombre del usuario es obligatorio");
        }
        if (dto.getCorreo() == null || dto.getCorreo().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "El correo electrónico es obligatorio");
        }

        String normalizedEmail = dto.getCorreo().trim().toLowerCase(Locale.ROOT);
        if (!normalizedEmail.matches("^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$")) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "El correo electrónico no tiene un formato válido");
        }
        if (usuarioRepository.existsByCorreo(normalizedEmail)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Este correo ya está registrado");
        }

        if (dto.getId() == null) {
            dto.setId(UUID.randomUUID());
        }
        if (dto.getActivo() == null) {
            dto.setActivo(true);
        }
        if (dto.getRol() == null || dto.getRol().isBlank()) {
            dto.setRol("Participante");
        }
        if (dto.getFechaRegistro() == null) {
            dto.setFechaRegistro(LocalDateTime.now());
        }
        dto.setCorreo(normalizedEmail);

        Usuario entity = usuarioMapper.toEntity(dto);

        if (dto.getContrasena() != null && !dto.getContrasena().isBlank()) {
            if (dto.getContrasena().length() < 8) {
                throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "La contraseña debe tener al menos 8 caracteres");
            }
            entity.setContrasenaHash(passwordService.hash(dto.getContrasena()));
        }

        Usuario saved = usuarioRepository.save(entity);
        return usuarioMapper.toDto(saved);
    }

    @Override
    public UsuarioDto update(UUID id, UsuarioDto dto) {
        if (dto == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Los datos de actualización son requeridos");
        }
        Usuario existing = usuarioRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Usuario no encontrado"));

        if (dto.getNombre() != null && !dto.getNombre().isBlank()) {
            existing.setNombre(dto.getNombre());
        }
        if (dto.getCorreo() != null && !dto.getCorreo().isBlank()) {
            String normalizedEmail = dto.getCorreo().trim().toLowerCase(Locale.ROOT);
            if (!normalizedEmail.equals(existing.getCorreo()) && usuarioRepository.existsByCorreo(normalizedEmail)) {
                throw new ResponseStatusException(HttpStatus.CONFLICT, "El correo ya está en uso por otro usuario");
            }
            existing.setCorreo(normalizedEmail);
        }
        if (dto.getActivo() != null) {
            existing.setActivo(dto.getActivo());
        }
        if (dto.getRol() != null && !dto.getRol().isBlank()) {
            existing.setRol(dto.getRol());
        }
        if (dto.getContrasena() != null && !dto.getContrasena().isBlank()) {
            if (dto.getContrasena().length() < 8) {
                throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "La contraseña debe tener al menos 8 caracteres");
            }
            existing.setContrasenaHash(passwordService.hash(dto.getContrasena()));
        }

        Usuario updated = usuarioRepository.save(existing);
        return usuarioMapper.toDto(updated);
    }

    @Override
    public void delete(UUID id) {
        if (!usuarioRepository.existsById(id)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Usuario no encontrado");
        }
        usuarioRepository.deleteById(id);
    }
}
