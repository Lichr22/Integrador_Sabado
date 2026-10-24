package cesde.integrador.controller;

import cesde.integrador.dto.RetoDto;
import cesde.integrador.service.RetoService;
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
@RequestMapping("/api/v1/retos")
public class RetoController {

    private final RetoService retoService;

    public RetoController(RetoService retoService) {
        this.retoService = retoService;
    }

    @GetMapping
    public ResponseEntity<List<RetoDto>> getAll() {
        return ResponseEntity.ok(retoService.getAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<RetoDto> getById(@PathVariable UUID id) {
        return ResponseEntity.ok(retoService.getById(id));
    }

    @PostMapping
    public ResponseEntity<RetoDto> create(@RequestBody RetoDto dto) {
        RetoDto created = retoService.create(dto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<RetoDto> update(@PathVariable UUID id, @RequestBody RetoDto dto) {
        RetoDto updated = retoService.update(id, dto);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        retoService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
