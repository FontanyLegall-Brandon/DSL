package kernel.logic.statements.action;

import kernel.generator.Visitable;
import kernel.generator.Visitor;
import kernel.model.brick.Brick;

public class Serial implements Visitable {

    private final String name;
    private final int baudrate;

    public Serial(String name, int baudrate) {
        this.name = name;
        this.baudrate = baudrate;
    }

    @Override
    public void accept(Visitor visitor) {
        visitor.visit(this);
    }

    public String initCode() {
        return String.format("\tSerial.begin(%s);\n", this.baudrate);
    }

    @Override
    public String declarationVarCode() {
        return "";
    }

}