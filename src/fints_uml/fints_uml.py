from datetime import datetime
import glob
import os
import re
import requests
import sys


def filter_hbci(binary_message):
    # according to "FinTS-Basiszeichensätze" in Formals
    invalidHbciChars = re.compile(b"[^\x20-\x7E\xA1-\xFF\x0A\x0D]")
    # replace illegal characters
    filtered = re.sub(invalidHbciChars, b".", binary_message)
    # add line breaks between segments (except the last one); does not handle nested segments
    separateSegments = re.compile(b"'(?=.)")
    filtered = re.sub(separateSegments, b"'\n", filtered)
    return filtered


def get_parts_from_sfbk(filename):
    """gets time, send/receive info and message content from kernel trace file

    returns list of tuples in format (datetime, 0/1, message)
    """
    r = re.compile(r"\d+_(?P<time>\d{8,8})_\d+(?:_)?(?P<send_receive_flag>[rs])r\.hbc")
    match = r.match(os.path.split(filename)[-1])
    if match is None:
        raise RuntimeError("invalid filename pattern from " + filename)
    dt = datetime.strptime(match["time"], "%H%M%S%f")
    send_receive = 0 if match["send_receive_flag"] == "r" else 1

    f = open(filename, "rb")
    binary_message = filter_hbci(f.read())

    return (dt, send_receive, binary_message)


def get_parts_from_sfpc(filename):
    f = open(filename, "rb")
    binary_message = filter_hbci(f.read())

    hbciRegex = re.compile(
        br"(?:.\r?\n)*?(?:Start HBCI message;\d+;(?P<send_receive_flag>[01]);\w+: (?P<time>[\d:.,]*);.*?\r?\n(?P<hbci>.*?)\r?\nEnd HBCI message)+",
        re.DOTALL,
    )
    matches_it = hbciRegex.finditer(binary_message)
    if not matches_it:
        raise RuntimeError("could not extract message data from file " + filename)

    send_receive_flags = []
    transaction_times = []
    messages_filtered = []
    for m in matches_it:
        send_receive_flags.append(int(m["send_receive_flag"].decode("utf-8")))
        transaction_times.append(datetime.strptime(m["time"].decode("utf-8"), "%H:%M:%S.%f"))
        messages_filtered.append(filter_hbci(m["hbci"]))

    return list(zip(transaction_times, send_receive_flags, messages_filtered))


def get_image_from_plantuml(plantuml_src, file_format):
    # use GET with hex encoding (~h)
    server_url = f"http://localhost:8080/{file_format}/~h"
    # note that the get request might fail if source is too long
    r = requests.get(server_url + bytearray(plantuml_src, "latin1").hex())
    r.raise_for_status()
    return r.content


def build_plantuml_from_messages(messages_list):
    # regroups the participants in its own list and removes duplicates via set
    # then make it a list again so that an appended FinTS participant is the last element
    participant_names = list(set(list(zip(*messages_list))[0]))
    fints_name = "FinTS"
    participant_names.append(fints_name)

    # header
    diagram_lines = [f"@startuml\n\n"]
    for p in participant_names:
        diagram_lines.append(f"participant {p}\n")
    # transactions
    for participant, datetime_, send_receive, binary_message in messages_list:
        arrow_str = "->" if send_receive == 1 else "<-"
        diagram_lines.append(f"\n{participant} {arrow_str} {fints_name}: {datetime_}\n")
        diagram_lines.append(f"note over {participant}\n")
        diagram_lines.append(binary_message.decode("latin-1"))  # todo split overly long lines
        diagram_lines.append("\nend note\n")
    # end/footer
    diagram_lines.append("\n@enduml\n")

    diag_str = "".join(diagram_lines)
    return diag_str


def collect_messages_from_files(filenames):
    messages = []
    for filename in filenames:
        if filename.endswith(".hbc"):
            messages.append(tuple(("SFBK",)) + get_parts_from_sfbk(filename))
        elif filename.endswith(".pro"):
            for message in get_parts_from_sfpc(filename):
                messages.append(tuple(("SMPC",)) + message)
    messages.sort(key=lambda components: components[1])  # sort by date
    return messages


def run_pipeline(filenames, out_filename_base):
    print(f"processing {filenames}")

    messages = collect_messages_from_files(filenames)
    plantuml_src = build_plantuml_from_messages(messages)

    file_puml = open(out_filename_base + ".plantuml", "w")
    file_puml.write(plantuml_src)
    file_puml.close()

    # try/catch
    image = get_image_from_plantuml(plantuml_src, "svg")
    save_image = open(out_filename_base + ".svg", "wb")
    save_image.write(image)
    save_image.close()


def __get_filenames__(console_args):
    filenames = [filename for arg in console_args for filename in glob.glob(arg)]
    return sorted(filenames)


def main():
    if len(sys.argv) < 2:
        print("missing file name(s)")
        sys.exit(1)

    file_list = sys.argv[1:]
    filenames = __get_filenames__(file_list)
    if not filenames:
        print(f"no files found looking for {file_list}")
        sys.exit(1)

    out_filename_base = os.path.split(filenames[0])[0] + os.path.sep + "fintsUml-generated"
    run_pipeline(filenames, out_filename_base)


if __name__ == "__main__":
    main()
