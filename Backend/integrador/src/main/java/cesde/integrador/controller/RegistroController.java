package cesde.integrador.controller;

import cesde.integrador.dto.RegistroDto;
import cesde.integrador.service.RegistroService;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/registros")
public class RegistroController {

    private final RegistroService registroService;

    public RegistroController(RegistroService registroService) {
        this.registroService = registroService;
    }

    @GetMapping
    public ResponseEntity<List<RegistroDto>> getAll() {
        return ResponseEntity.ok(registroService.getAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<RegistroDto> getById(@PathVariable UUID id) {
        return ResponseEntity.ok(registroService.getById(id));
    }

    @PostMapping
    public ResponseEntity<RegistroDto> create(@RequestBody RegistroDto dto) {
        RegistroDto created = registroService.create(dto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<RegistroDto> update(@PathVariable UUID id, @RequestBody RegistroDto dto) {
        RegistroDto updated = registroService.update(id, dto);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        registroService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
