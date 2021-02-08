from datetime import datetime
import os
import re
import requests
import sys

def filter_hbci(binary_message):
    # according to "FinTS-Basiszeichensätze" in Formals
    invalidHbciChars = re.compile(b'[^\x20-\x7E\xA1-\xFF\x0A\x0D]')
    # replace illegal characters
    filtered = re.sub(invalidHbciChars, b'.', binary_message)
    # add line breaks between segments (except the last one); does not handle nested segments
    separateSegments = re.compile(b'\'(?=.)')
    filtered = re.sub(separateSegments, b'\'\n', filtered)
    return filtered
    
def get_parts_from_sfbk(filename):
    '''gets time, send/receive info and message content from kernel trace file
    
    returns list of tuples in format (datetime, 0/1, message)
    '''
    r = re.compile(r'\d+_(?P<date>\d{8,8})_\d+_(?P<send_receive_flag>[rs])r\.hbc')
    match = r.match(os.path.split(filename)[-1])
    if match is None:
        raise RuntimeError("invalid filename pattern from " + filename)
    dt = datetime.strptime(match['date'], '%H%M%S%f')
    send_receive = 0 if match['send_receive_flag'] == 'r' else 1

    f = open(filename, 'rb')
    binary_message = filter_hbci(f.read())

    return (dt, send_receive, binary_message)

def get_parts_from_sfpc(filename):
    f = open(filename, 'rb')
    binary_message = filter_hbci(f.read())

    hbciRegex = re.compile(rb"(?:Start HBCI message.*\n(.*?)\nEnd HBCI message\n)+?", re.MULTILINE)
    messages = hbciRegex.findall(binary_message)
    messages_filtered = [filter_hbci(m) for m in messages]
    
    return list(zip(
        [datetime.datetime.now()] * len(messages_filtered), # todo
        [0] * len(messages_filtered), # todo
        messages_filtered)
        )


def get_image_from_plantuml(plantuml_src, file_format):
    # use GET with hex encoding (~h)
    server_url = f'http://localhost:8080/{file_format}/~h'
    # note that the get request might fail if source is too long
    r = requests.get(server_url + bytearray(plantuml_src, "latin1").hex())
    print(r.status_code)
    r.raise_for_status()
    return r.content

def build_plantuml_from_messages(messages_list):
    # regroups the participants in its own list and removes duplicates via set
    # then make it a list again so that an appended FinTS participant is the last element
    participant_names = list(set(list(zip(*messages_list))[0]))
    fints_name = 'FinTS'
    participant_names.append(fints_name)

    # header
    diagram_lines = [f'@startuml\n\n']
    for p in participant_names:
        diagram_lines.append(f'participant {p}\n')
    # transactions
    for participant, datetime_, send_receive, binary_message in messages_list:
        arrow_str = '->' if send_receive == 1 else '<-'
        diagram_lines.append(f'{participant} {arrow_str} {fints_name}: {datetime_}\n')
        diagram_lines.append(f'note over {participant}\n')
        diagram_lines.append(binary_message.decode('latin-1'))
        diagram_lines.append('\nend note\n')
    # end/footer
    diagram_lines.append('\n@enduml\n')

    diag_str = ''.join(diagram_lines)
    return diag_str

def collect_messages_from_files(filenames):
    # also add sender to the list (smpc or kernel)
    messages = []
    for filename in filenames:
        if filename.endswith('.hbc'):
            messages.append(tuple(('SFBK',)) + get_parts_from_sfbk(filename))
        elif filename.endswith('.pro'):
            for message in get_parts_from_sfpc(filename):
                messages.append(tuple(('SMPC',)) + message)
    # todo sort by timestamp
    return messages


def run_pipeline(filenames):
    print(f'processing {filenames}')

    messages = collect_messages_from_files(filenames)
    plantuml_src = build_plantuml_from_messages(messages)

    out_filename_base = 'fintsUml-generated'
    file_puml = open(out_filename_base + '.plantuml', 'w')
    file_puml.write(plantuml_src)
    file_puml.close()

    # try/catch
    image = get_image_from_plantuml(plantuml_src, 'svg')
    save_image = open(out_filename_base + '.svg', 'wb')
    save_image.write(image)
    save_image.close()


def main():
    if len(sys.argv) < 2:
        print("missing file name(s)")
        sys.exit(1)        
    run_pipeline(sys.argv[1:])

if __name__ == "__main__":
    main()
