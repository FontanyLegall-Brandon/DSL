import static builder.ArduinoBuilder.analogicActuator;
import static builder.ArduinoBuilder.analogicSensor;
import static builder.ArduinoBuilder.arduino;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.util.HashMap;
import java.util.Map;
import kernel.ArduinoApp;
import kernel.generator.Generator;

public class Main {

  public static void main(String[] args) throws Exception {
    HashMap<String, Generator> arduinoAppGenerated = new HashMap<>();
    ArduinoApp arduinoApp;
    Generator generator;

    // ----------------
    // SCENARIO 1
    // ----------------

        /*
        SENSOR button 10
        ACTUATOR led 11
        ACTUATOR buzzer 9

        INIT off {
            SET led OFF
            SET buzzer OFF
            button == ON -> on
        }

        on {
            SET led ON
            SET buzzer ON
            button == OFF -> off
        }
         */

    arduinoApp =
        arduino("scenario1")
            .setup(analogicSensor("button", 10))
            .setup(analogicActuator("led", 11))
            .setup(analogicActuator("buzzer", 9))
              .states()
                .state("on")
                  .set("test").toHigh()
                  .sleep(10)
                  .set("test").toLow()
                  .when().ifIsEqual("button", "1").and().ifIsEqual("button", "1").thenGoToState("off")
                .state("off")
                  .set("test").toLow()
                  .when().ifIsEqual("button", "1").thenGoToState("on")
              .initState("off")
            .build();

    generator = new Generator();
    arduinoApp.accept(generator);
    arduinoAppGenerated.put(arduinoApp.getName(), generator);

    // ----------------
    // OLD
    // ----------------

        /*
        arduinoApp =
            arduino("monPremierCode2")
                .setup(sensor("led",2))
                .setup(actuator("button",3))
                .setup(lcd("lcd_0", 2))

                .stateTable()
                .state("on","led").when("button").isHigh().thenState("off","led")
                .state("off","led").when("button").isHigh().thenState("on","led")
                .endStateTable()
                .build();

        generator = new Generator();
        arduinoApp.accept(generator);
        arduinoAppGenerated.put(arduinoApp.getName(), generator);
        */

    try {
      new File("out/").mkdir();

      for (Map.Entry<String, Generator> entry : arduinoAppGenerated.entrySet()) {
        PrintWriter writer = new PrintWriter("out/" + entry.getKey() + ".ino", "UTF-8");
        writer.print(entry.getValue().getGeneratedCode());
        writer.close();
      }

    } catch (UnsupportedEncodingException | FileNotFoundException e) {
      e.printStackTrace();
    }
  }

}
