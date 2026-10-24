package cesde.integrador.controller;

import cesde.integrador.dto.EmpresaDto;
import cesde.integrador.service.EmpresaService;
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
@RequestMapping("/api/v1/empresas")
public class EmpresaController {

    private final EmpresaService empresaService;

    public EmpresaController(EmpresaService empresaService) {
        this.empresaService = empresaService;
    }

    @GetMapping
    public ResponseEntity<List<EmpresaDto>> getAll() {
        return ResponseEntity.ok(empresaService.getAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<EmpresaDto> getById(@PathVariable UUID id) {
        return ResponseEntity.ok(empresaService.getById(id));
    }

    @PostMapping
    public ResponseEntity<EmpresaDto> create(@RequestBody EmpresaDto dto) {
        EmpresaDto created = empresaService.create(dto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<EmpresaDto> update(@PathVariable UUID id, @RequestBody EmpresaDto dto) {
        EmpresaDto updated = empresaService.update(id, dto);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        empresaService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
