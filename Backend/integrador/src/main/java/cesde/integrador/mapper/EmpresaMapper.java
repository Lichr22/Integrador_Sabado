package cesde.integrador.mapper;

import cesde.integrador.dto.EmpresaDto;
import cesde.integrador.entity.Empresa;
import java.util.List;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface EmpresaMapper {

    EmpresaDto toDto(Empresa entity);

    Empresa toEntity(EmpresaDto dto);

    List<EmpresaDto> toDtoList(List<Empresa> entities);
}
