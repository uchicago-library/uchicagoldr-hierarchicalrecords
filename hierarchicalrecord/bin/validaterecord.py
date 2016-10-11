from json import dumps
from argparse import ArgumentParser

from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord
from hierarchicalrecord.recordconf import RecordConf
from hierarchicalrecord.recordvalidator import RecordValidator


def make_validator(conf_fp):
    conf = RecordConf()
    conf.from_csv(conf_fp)
    return RecordValidator(conf)


def validate_record(record, validator):
    validation = validator.validate(record)
    return validation


def pprint_result(validation, just_result=False):
    pp_result = {"valid": validation[0],
                 "errors": validation[1]}
    if not just_result:
        print(dumps(pp_result, indent=4))
    else:
        q_pp_result = {"valid": pp_result['valid']}
        print(dumps(q_pp_result, indent=4))


def main():
    parser = ArgumentParser(description="A quick hierarchicalrecord " +
                            "validation script.")
    parser.add_argument(
        "record_filepath",
        type=str,
        help="The file path to the record"
    )
    parser.add_argument(
        "config_filepath",
        type=str,
        help="The file path to the config"
    )
    parser.add_argument(
        "--just-result",
        action="store_true",
        help="Print only the result, not any potential validation errors.",
        default=False
    )

    args = parser.parse_args()

    v = make_validator(args.config_filepath)
    r = HierarchicalRecord(from_file=args.record_filepath)
    result = validate_record(r, v)
    pprint_result(result, just_result=args.just_result)


if __name__ == "__main__":
    main()
