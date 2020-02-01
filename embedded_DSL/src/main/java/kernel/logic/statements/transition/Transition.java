package kernel.logic.statements.transition;

import kernel.generator.Visitable;
import kernel.generator.Visitor;
import kernel.logic.State;
import lombok.Data;
import lombok.Getter;

@Data
public class Transition implements Visitable {

  String condition;
  State destination;

  public void accept(Visitor visitor) {
    visitor.visit(this);
  }

  @Override
  public String initCode() {
    return null;
  }

  @Override
  public String declarationVarCode() {
    return null;
  }
}
