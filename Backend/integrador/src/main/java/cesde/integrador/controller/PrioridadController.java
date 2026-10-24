package cesde.integrador.controller;

import cesde.integrador.dto.PrioridadDto;
import cesde.integrador.service.PrioridadService;
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
@RequestMapping("/api/v1/prioridades")
public class PrioridadController {

    private final PrioridadService prioridadService;

    public PrioridadController(PrioridadService prioridadService) {
        this.prioridadService = prioridadService;
    }

    @GetMapping
    public ResponseEntity<List<PrioridadDto>> getAll() {
        return ResponseEntity.ok(prioridadService.getAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<PrioridadDto> getById(@PathVariable UUID id) {
        return ResponseEntity.ok(prioridadService.getById(id));
    }

    @PostMapping
    public ResponseEntity<PrioridadDto> create(@RequestBody PrioridadDto dto) {
        PrioridadDto created = prioridadService.create(dto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<PrioridadDto> update(@PathVariable UUID id, @RequestBody PrioridadDto dto) {
        PrioridadDto updated = prioridadService.update(id, dto);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        prioridadService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
